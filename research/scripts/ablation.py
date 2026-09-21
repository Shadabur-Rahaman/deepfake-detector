#!/usr/bin/env python3
"""Ablation: individual baselines vs corrected named-weight ensemble."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np

from _lib import (
    REPO_ROOT,
    binary_metrics,
    ensure_repo_on_path,
    expected_calibration_error,
    load_config,
    resolve_path,
    save_json,
    set_seed,
)


def main() -> None:
    cfg = load_config()
    set_seed(int(cfg["seed"]))
    ensure_repo_on_path()

    from services.confidence_aggregator_2025 import (
        compute_weighted_fake_probability,
        to_fake_probability,
    )

    pred_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "evaluation"
    out_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "ablation"
    out_dir.mkdir(parents=True, exist_ok=True)

    weights = cfg["ensemble"]["weights"]
    model_preds = {}
    labels_ref = None
    paths_ref = None

    for name in weights.keys():
        path = pred_dir / f"predictions_{name}.json"
        if not path.exists():
            print(f"[SKIP] missing {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        model_preds[name] = data
        if labels_ref is None:
            labels_ref = np.asarray(data["labels"], dtype=int)
            paths_ref = data["paths"]
        else:
            # Align on intersection of paths
            assert data["paths"] == paths_ref, "Prediction path lists must match for ablation"

    if len(model_preds) < 1:
        raise SystemExit("No prediction files found — run evaluate_models.py first")

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["seed"],
        "n": int(len(labels_ref)),
        "baselines": {},
        "ensembles": {},
        "notes": [
            "Baselines use each checkpoint's sigmoid fake probability on A/test.",
            "Corrected ensemble converts label-confidence semantics via to_fake_probability "
            "then applies normalize_named_weights (here probs are already P(fake)).",
            "Equal-weight ensemble is an additional control.",
        ],
    }

    # Individual baselines
    for name, data in model_preds.items():
        probs = np.asarray(data["fake_probabilities"], dtype=float)
        report["baselines"][name] = {
            "metrics": binary_metrics(labels_ref, probs, cfg["threshold"]),
            "ece": expected_calibration_error(labels_ref, probs, cfg["calibration"]["n_bins"]),
            "configured_weight": weights.get(name),
        }

    # Per-sample named predictions for corrected aggregator.
    # Since model outputs are already P(fake), express as FAKE+conf=p or REAL+conf=1-p.
    n = len(labels_ref)
    corrected_probs = []
    equal_probs = []
    used_weights_last = None
    for i in range(n):
        named = {}
        for name, data in model_preds.items():
            p = float(data["fake_probabilities"][i])
            if p >= 0.5:
                named[name] = ("Deepfake Detected", p)
            else:
                named[name] = ("Real Video", 1.0 - p)
        ens_p, used, _ = compute_weighted_fake_probability(named, weights)
        used_weights_last = used
        corrected_probs.append(ens_p)

        # equal weight control
        ens_eq, _, _ = compute_weighted_fake_probability(named, None)
        equal_probs.append(ens_eq)

        # sanity: to_fake_probability round-trip
        for name, (lab, conf) in named.items():
            assert abs(to_fake_probability(lab, conf) - float(model_preds[name]["fake_probabilities"][i])) < 1e-9

    corrected_probs = np.asarray(corrected_probs)
    equal_probs = np.asarray(equal_probs)

    report["ensembles"]["corrected_named_weights"] = {
        "weights_configured": weights,
        "weights_normalized_example": used_weights_last,
        "metrics": binary_metrics(labels_ref, corrected_probs, cfg["threshold"]),
        "ece": expected_calibration_error(labels_ref, corrected_probs, cfg["calibration"]["n_bins"]),
    }
    report["ensembles"]["equal_weight"] = {
        "metrics": binary_metrics(labels_ref, equal_probs, cfg["threshold"]),
        "ece": expected_calibration_error(labels_ref, equal_probs, cfg["calibration"]["n_bins"]),
    }

    # Mean-probability naive average (no label conversion — already P(fake))
    stacked = np.stack([np.asarray(model_preds[n]["fake_probabilities"]) for n in model_preds], axis=0)
    mean_p = stacked.mean(axis=0)
    report["ensembles"]["mean_probability"] = {
        "metrics": binary_metrics(labels_ref, mean_p, cfg["threshold"]),
        "ece": expected_calibration_error(labels_ref, mean_p, cfg["calibration"]["n_bins"]),
    }

    save_json(out_dir / "ablation_report.json", report)
    save_json(out_dir / "ensemble_predictions.json", {
        "paths": paths_ref,
        "labels": labels_ref.tolist(),
        "corrected_named_weights": corrected_probs.tolist(),
        "equal_weight": equal_probs.tolist(),
        "mean_probability": mean_p.tolist(),
    })

    for k, v in report["baselines"].items():
        m = v["metrics"]
        print(f"baseline {k}: acc={m['accuracy']:.4f} f1={m['f1']:.4f} auc={m['roc_auc']}")
    for k, v in report["ensembles"].items():
        m = v["metrics"]
        print(f"ensemble {k}: acc={m['accuracy']:.4f} f1={m['f1']:.4f} auc={m['roc_auc']}")
    print(f"Wrote {out_dir / 'ablation_report.json'}")


if __name__ == "__main__":
    main()
