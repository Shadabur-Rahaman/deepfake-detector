"""
Focused deterministic tests for the Stage-1 ensemble correctness patch.

Covers:
- same-category models do not overwrite each other
- REAL .80 confidence → fake_probability .20
- toy example → .67
- weight normalization
- invalid weight handling
- probability bounding
- hybrid receives named configured weights
- existing ModelType-keyed calls still work
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

# Allow `from services...` and `from app.services...` depending on cwd
BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = Path(__file__).resolve().parents[1]
for p in (str(BACKEND_ROOT), str(APP_ROOT), str(APP_ROOT.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from services.confidence_aggregator_2025 import (
        ModelType,
        FaceQualityMetrics,
        TemporalConsistencyMetrics,
        ConfidenceAggregator2025,
        to_fake_probability,
        normalize_named_weights,
        compute_weighted_fake_probability,
        aggregate_hybrid_detection_scores,
        sanitize_weight,
    )
except ImportError:
    from app.services.confidence_aggregator_2025 import (
        ModelType,
        FaceQualityMetrics,
        TemporalConsistencyMetrics,
        ConfidenceAggregator2025,
        to_fake_probability,
        normalize_named_weights,
        compute_weighted_fake_probability,
        aggregate_hybrid_detection_scores,
        sanitize_weight,
    )


def _neutral_quality() -> FaceQualityMetrics:
    return FaceQualityMetrics(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)


def _neutral_temporal() -> TemporalConsistencyMetrics:
    return TemporalConsistencyMetrics(1.0, 1.0, 1.0, 0.0)


class TestFakeProbability:
    def test_real_080_becomes_fake_020(self):
        assert to_fake_probability("Real Video", 0.80) == pytest.approx(0.20)
        assert to_fake_probability("Authentic Video", 0.80) == pytest.approx(0.20)
        assert to_fake_probability("Real Face", 0.80) == pytest.approx(0.20)

    def test_fake_keeps_confidence(self):
        assert to_fake_probability("Deepfake Detected", 0.90) == pytest.approx(0.90)
        assert to_fake_probability("AI-Generated Content", 0.70) == pytest.approx(0.70)

    def test_probabilities_bounded(self):
        assert 0.0 <= to_fake_probability("Real", 1.5) <= 1.0
        assert 0.0 <= to_fake_probability("Deepfake", -0.2) <= 1.0
        assert 0.0 <= to_fake_probability("Real", float("nan")) <= 1.0
        # Non-finite confidence falls back to 0.5 label-confidence → Real → fake_p=0.5
        assert to_fake_probability("Real", float("inf")) == pytest.approx(0.5)
        assert to_fake_probability("Deepfake Detected", float("-inf")) == pytest.approx(0.5)


class TestWeightNormalization:
    def test_weights_are_normalized(self):
        weights = normalize_named_weights(["A", "B", "C"], {"A": 0.60, "B": 0.30, "C": 0.10})
        assert sum(weights.values()) == pytest.approx(1.0)
        assert weights["A"] == pytest.approx(0.60)
        assert weights["B"] == pytest.approx(0.30)
        assert weights["C"] == pytest.approx(0.10)

    def test_unnormalized_input_normalized(self):
        weights = normalize_named_weights(["A", "B"], {"A": 2.0, "B": 2.0})
        assert weights["A"] == pytest.approx(0.5)
        assert weights["B"] == pytest.approx(0.5)

    def test_invalid_weights_handled_safely(self):
        weights = normalize_named_weights(
            ["A", "B", "C"],
            {"A": float("nan"), "B": -1.0, "C": float("inf")},
        )
        assert sum(weights.values()) == pytest.approx(1.0)
        # All invalid → equal weights
        assert weights["A"] == pytest.approx(1.0 / 3.0)
        assert weights["B"] == pytest.approx(1.0 / 3.0)
        assert weights["C"] == pytest.approx(1.0 / 3.0)

    def test_zero_weights_become_equal(self):
        weights = normalize_named_weights(["A", "B"], {"A": 0.0, "B": 0.0})
        assert weights["A"] == pytest.approx(0.5)
        assert weights["B"] == pytest.approx(0.5)

    def test_sanitize_weight(self):
        assert sanitize_weight(None) == 1.0
        assert sanitize_weight(float("nan")) == 1.0
        assert sanitize_weight(-3) == 1.0
        assert sanitize_weight(0.4) == pytest.approx(0.4)


class TestToyExample:
    def test_toy_example_produces_067(self):
        """
        A = FAKE .90 w=.60
        B = REAL .80 w=.30  → fake_p=.20
        C = FAKE .70 w=.10
        → .60*.90 + .30*.20 + .10*.70 = .67
        """
        preds = {
            "A": ("Deepfake Detected", 0.90),
            "B": ("Real Video", 0.80),
            "C": ("Deepfake Detected", 0.70),
        }
        weights = {"A": 0.60, "B": 0.30, "C": 0.10}
        fake_p, used, per_model = compute_weighted_fake_probability(preds, weights)
        assert per_model["A"] == pytest.approx(0.90)
        assert per_model["B"] == pytest.approx(0.20)
        assert per_model["C"] == pytest.approx(0.70)
        assert fake_p == pytest.approx(0.67)
        assert sum(used.values()) == pytest.approx(1.0)


class TestNoCategoryCollision:
    def test_same_category_models_do_not_overwrite(self):
        aggregator = ConfidenceAggregator2025(device="cpu")
        preds = {
            "efficientnet_b0": ("Deepfake Detected", 0.90),
            "efficientnet_b4": ("Real Video", 0.80),
            "efficientnet_b7": ("Deepfake Detected", 0.70),
        }
        weights = {
            "efficientnet_b0": 0.60,
            "efficientnet_b4": 0.30,
            "efficientnet_b7": 0.10,
        }
        result = aggregator.aggregate_ensemble_predictions(
            preds,
            _neutral_quality(),
            _neutral_temporal(),
            named_weights=weights,
        )
        breakdown = result.detailed_breakdown
        assert set(breakdown["model_predictions"].keys()) == set(preds.keys())
        assert breakdown["fake_probability"] == pytest.approx(0.67)
        assert len(breakdown["model_weights"]) == 3


class TestHybridNamedWeights:
    def test_hybrid_receives_named_configured_weights(self):
        detection_scores = [
            ("ultra_ensemble_25", 0.80, 0.18),
            ("gemini_api", 0.20, 0.10),
            ("free_ai_ensemble", 0.60, 0.17),
        ]
        fake_p, norm_weights = aggregate_hybrid_detection_scores(detection_scores)
        assert set(norm_weights.keys()) == {"ultra_ensemble_25", "gemini_api", "free_ai_ensemble"}
        assert sum(norm_weights.values()) == pytest.approx(1.0)
        # Relative proportions preserved
        assert norm_weights["ultra_ensemble_25"] > norm_weights["gemini_api"]
        assert 0.0 <= fake_p <= 1.0

    def test_hybrid_invalid_weights_safe(self):
        detection_scores = [
            ("a", 0.9, float("nan")),
            ("b", 0.1, -5.0),
        ]
        fake_p, norm_weights = aggregate_hybrid_detection_scores(detection_scores)
        assert math.isfinite(fake_p)
        assert 0.0 <= fake_p <= 1.0
        assert sum(norm_weights.values()) == pytest.approx(1.0)


class TestBackwardCompatibleModelTypeCalls:
    def test_existing_modeltype_keyed_calls_still_work(self):
        aggregator = ConfidenceAggregator2025(device="cpu")
        preds = {
            ModelType.EFFICIENTNET: ("Deepfake Detected", 0.90),
            ModelType.RESNET: ("Real Video", 0.80),
            ModelType.VISION_TRANSFORMER: ("Deepfake Detected", 0.70),
        }
        result = aggregator.aggregate_ensemble_predictions(
            preds,
            _neutral_quality(),
            _neutral_temporal(),
        )
        assert result.prediction in ("Deepfake Detected", "Real Video", "Uncertain")
        assert result.confidence is None or (0.0 <= result.confidence <= 1.0)
        # Keys preserved as enum value strings
        names = set(result.detailed_breakdown["model_predictions"].keys())
        assert "efficientnet" in names
        assert "resnet" in names
        assert "vision_transformer" in names


class TestAsyncAggregationPreservesNames:
    def test_async_aggregator_forwards_named_weights(self):
        from services.async_ensemble_processor_2025 import (
            AsyncEnsembleProcessor2025,
            ModelExecutionResult,
            ModelExecutionStatus,
        )

        processor = AsyncEnsembleProcessor2025()
        results = [
            ModelExecutionResult(
                model_name="efficientnet_b0",
                prediction="Deepfake Detected",
                confidence=0.90,
                logits=None,
                execution_time=0.01,
                status=ModelExecutionStatus.COMPLETED,
            ),
            ModelExecutionResult(
                model_name="efficientnet_b4",
                prediction="Real Video",
                confidence=0.80,
                logits=None,
                execution_time=0.01,
                status=ModelExecutionStatus.COMPLETED,
            ),
            ModelExecutionResult(
                model_name="efficientnet_b7",
                prediction="Deepfake Detected",
                confidence=0.70,
                logits=None,
                execution_time=0.01,
                status=ModelExecutionStatus.COMPLETED,
            ),
        ]
        weights = {
            "efficientnet_b0": 0.60,
            "efficientnet_b4": 0.30,
            "efficientnet_b7": 0.10,
        }
        out = processor._aggregate_ensemble_results(results, model_weights=weights)
        assert set(out.predictions.keys()) == {
            "efficientnet_b0",
            "efficientnet_b4",
            "efficientnet_b7",
        }
        # Ensemble fake probability for toy = 0.67 → Deepfake with confidence scaled by quality
        assert out.ensemble_prediction == "Deepfake Detected"
        # With neutral quality 0.5 in async path, confidence is scaled; check decision direction via score
        # Reconstruct expected fake_p from named outputs
        fake_p, _, _ = compute_weighted_fake_probability(
            {k: v for k, v in out.predictions.items()},
            weights,
        )
        assert fake_p == pytest.approx(0.67)
