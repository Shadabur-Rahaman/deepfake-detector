# app/services/ultra_ensemble.py
"""
Ultra-Ensemble Deepfake Detector
================================
Combines five complementary models:

1. EfficientNet-B0      – baseline (spatial artefacts)
2. MesoNet              – mesoscopic deepfake cues
3. Free-AI Ensemble     – (optional) open-source boosters
4. Enhanced Detector    – any proprietary advanced model
5. Vision Transformer   – global-context attention

The detector is *self-configuring*: it only uses models that are
actually available in your environment.
"""

from __future__ import annotations
import asyncio, logging, importlib
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────
# Helper: lazy imports so the file never crashes if a model is missing
# ──────────────────────────────────────────────────────────────────────────
def _safe_import(path: str, attr: str | None = None):
    try:
        mod = importlib.import_module(path)
        return getattr(mod, attr) if attr else mod
    except (ImportError, AttributeError):
        logger.warning(f"⚠️  {path} not available – skipped")
        return None


# ──────────────────────────────────────────────────────────────────────────
# Main class
# ──────────────────────────────────────────────────────────────────────────
class UltraEnsembleDetector:
    """
    Usage
    -----
    >>> detector = UltraEnsembleDetector()
    >>> result = await detector.ultra_detect(faces, video_path)
    """
    # ✅ BIAS FIX: Balanced weight distribution for unbiased detection
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "efficientnet": 0.20,  # Reduced from 0.25
        "mesonet":      0.20,  # Reduced from 0.25
        "free_ai":      0.20,  # Same
        "enhanced":     0.20,  # Increased from 0.15
        "vit":          0.20,  # Increased from 0.15
    }

    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.models: Dict[str, object] = {}         # loaded detectors
        self.initialised = False

    # ───────────────────────────────────────────────────────────────
    #  Model loading
    # ───────────────────────────────────────────────────────────────
    async def _initialise(self):
        """Load every detector that is physically present in the repo."""
        if self.initialised:
            return

        logger.info("🌀 UltraEnsemble: loading detectors …")

        # 1) EfficientNet (always present)
        deepfake = _safe_import("app.services.deepfake_detector", "detect_deepfake_in_frames")
        if deepfake:
            self.models["efficientnet"] = deepfake

        # 2) MesoNet
        mesonet_cls = _safe_import("app.models.mesonet_detector", "MesoNetDetector")
        if mesonet_cls:
            self.models["mesonet"] = mesonet_cls()

        # 3) Free-AI boosters
        free_ai_mod = _safe_import("app.services.free_ai_boosters")
        if free_ai_mod:
            self.models["free_ai"] = free_ai_mod

        # 4) Enhanced detector
        enh_cls = _safe_import("app.services.enhanced_detection_engine", "EnhancedDetectionEngine")
        if enh_cls:
            self.models["enhanced"] = enh_cls()

        # 5) Vision Transformer
        vit_cls = _safe_import("app.models.spatial_analysis.vision_transformer", "ViTSpatialAnalyzer")
        if vit_cls:
            self.models["vit"] = vit_cls()

        self.initialised = True
        logger.info(f"✅ UltraEnsemble initialised → {list(self.models.keys())}")

    # ───────────────────────────────────────────────────────────────
    #  Single-model execution helpers
    # ───────────────────────────────────────────────────────────────
    async def _run_efficientnet(self, func, faces):
        pred, conf = await func(faces)
        score = conf if "Deepfake" in pred else (1.0 - conf)
        return score

    async def _run_mesonet(self, model, faces):
        res = await model.predict(faces)
        score = res["confidence"] if res["prediction"] == "Deepfake" else (1.0 - res["confidence"])
        return score

    async def _run_free_ai(self, mod, faces, video_path):
        # expect coroutine returning {'prediction','confidence'}
        res = await mod.ultra_analyze_faces(faces, video_path)
        conf = res.get("confidence", 50) / 100.0
        score = conf if res.get("prediction", "").lower().startswith("deep") else (1.0 - conf)
        return score

    async def _run_enhanced(self, model, faces):
        res = await model.enhanced_detect(faces, video_path)
        conf = res.get("confidence", 50) / 100.0
        score = conf if "Deepfake" in res.get("prediction", "") else (1.0 - conf)
        return score

    async def _run_vit(self, model, faces):
        res = await model.analyze(faces)
        conf = res.get("confidence", 50)
        if conf > 1.0:  # percentage
            conf /= 100.0
        score = conf if "Deepfake" in res.get("prediction", "") else (1.0 - conf)
        return score

    # Dispatcher
    async def _model_score(self, name: str, faces, video_path):
        model = self.models[name]
        if name == "efficientnet":
            return await self._run_efficientnet(model, faces)
        if name == "mesonet":
            return await self._run_mesonet(model, faces)
        if name == "free_ai":
            return await self._run_free_ai(model, faces, video_path)
        if name == "enhanced":
            return await self._run_enhanced(model, faces)
        if name == "vit":
            return await self._run_vit(model, faces)
        return 0.5   # neutral fallback

    # ───────────────────────────────────────────────────────────────
    #  Public API
    # ───────────────────────────────────────────────────────────────
    async def ultra_detect(self, faces, video_path: str | None = None) -> Dict:
        """
        faces: list[torch.Tensor (3,224,224)]
        Returns:
            {
              'prediction': str,
              'confidence': float(0-100),
              'models_used': list[str],
              'ensemble_score': float(0-1)
            }
        """
        await self._initialise()
        if not faces:
            return {"prediction": "No Faces Detected", "confidence": 0.0}

        # launch model tasks in parallel
        tasks = {
            name: asyncio.create_task(self._model_score(name, faces, video_path))
            for name in self.models
        }
        await asyncio.gather(*tasks.values())

        # ensemble
        total_score = 0.0
        total_weight = 0.0
        model_breakdown: Dict[str, Tuple[float, float]] = {}   # name → (score, weight)

        for name, task in tasks.items():
            score = task.result()
            weight = self.weights.get(name, 0.1)
            total_score += score * weight
            total_weight += weight
            model_breakdown[name] = (round(score, 3), weight)

        if total_weight == 0:
            return {"prediction": "Analysis Failed", "confidence": 0.0}

        final_score = total_score / total_weight          # 0 = real, 1 = deepfake
        deepfake_prob = final_score
        real_prob = 1 - final_score

        prediction = "Deepfake Detected" if deepfake_prob >= 0.5 else "Real Video"
        confidence = round(max(deepfake_prob, real_prob) * 100, 1)
        confidence = min(confidence, 98.0)               # cap

        return {
            "prediction": prediction,
            "confidence": confidence,
            "models_used": list(model_breakdown.keys()),
            "ensemble_score": round(final_score, 3),
            "model_contributions": model_breakdown,
        }
