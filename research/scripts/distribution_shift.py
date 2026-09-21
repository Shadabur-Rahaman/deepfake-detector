#!/usr/bin/env python3
"""Distribution-shift probe: train/val domain A metrics vs test on dataset B."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from _lib import (
    binary_metrics,
    expected_calibration_error,
    load_checkpoint_model,
    load_config,
    resolve_path,
    run_inference,
    save_json,
    set_seed,
)


def _samples(block):
    return [(s["path"], int(s["label"])) for s in block["samples"]]


def main() -> None:
    cfg = load_config()
    set_seed(int(cfg["seed"]))
    with open(resolve_path(cfg["paths"]["manifests_dir"]) / "dataset_manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "distribution_shift"
    out_dir.mkdir(parents=True, exist_ok=True)

    test_a = _samples(manifest["dataset_A"]["splits"]["test"])
    test_b = _samples(manifest["dataset_B"]["shift_test"])

    if not test_b:
        save_json(out_dir / "shift_report.json", {
            "status": "skipped",
            "reason": "Dataset B has no usable labeled images",
        })
        print("Skipped: no Dataset B samples")
        return

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["seed"],
        "device": device,
        "protocol": "Models trained historically on faces derived from Dataset A family; "
                    "evaluate A/test vs B/shift_test without refitting.",
        "n_test_A": len(test_a),
        "n_test_B": len(test_b),
        "models": {},
    }

    for name, meta in cfg["checkpoints"].items():
        if not meta.get("enabled", True):
            continue
        ckpt = resolve_path(meta["path"])
        if not ckpt.exists():
            continue
        try:
            model, load_info = load_checkpoint_model(ckpt, device)
            a = run_inference(model, test_a, device, cfg["image_size"], cfg["batch_size"])
            b = run_inference(model, test_b, device, cfg["image_size"], cfg["batch_size"])
            ma = binary_metrics(a.labels, a.probs, cfg["threshold"])
            mb = binary_metrics(b.labels, b.probs, cfg["threshold"])
            report["models"][name] = {
                "status": "ok",
                "load_info": load_info,
                "on_A_test": {
                    "metrics": ma,
                    "ece": expected_calibration_error(a.labels, a.probs, cfg["calibration"]["n_bins"]),
                    "inference_seconds": a.inference_seconds,
                },
                "on_B_shift_test": {
                    "metrics": mb,
                    "ece": expected_calibration_error(b.labels, b.probs, cfg["calibration"]["n_bins"]),
                    "inference_seconds": b.inference_seconds,
                },
                "delta_accuracy_B_minus_A": mb["accuracy"] - ma["accuracy"],
                "delta_f1_B_minus_A": mb["f1"] - ma["f1"],
                "delta_roc_auc_B_minus_A": (
                    None if ma["roc_auc"] is None or mb["roc_auc"] is None
                    else mb["roc_auc"] - ma["roc_auc"]
                ),
            }
            print(
                f"[OK] {name}: A acc={ma['accuracy']:.4f} → B acc={mb['accuracy']:.4f} "
                f"(Δ={mb['accuracy']-ma['accuracy']:+.4f})"
            )
        except Exception as e:
            report["models"][name] = {"status": "failed", "error": str(e)}
            print(f"[FAIL] {name}: {e}")

    save_json(out_dir / "shift_report.json", report)
    print(f"Wrote {out_dir / 'shift_report.json'}")


if __name__ == "__main__":
    main()
