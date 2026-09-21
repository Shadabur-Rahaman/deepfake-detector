#!/usr/bin/env python3
"""Evaluate loadable checkpoints on the held-out test split."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

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


def _load_manifest(cfg):
    path = resolve_path(cfg["paths"]["manifests_dir"]) / "dataset_manifest.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _samples(split_block):
    return [(s["path"], int(s["label"])) for s in split_block["samples"]]


def main() -> None:
    cfg = load_config()
    set_seed(int(cfg["seed"]))
    manifest = _load_manifest(cfg)

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "evaluation"
    fig_dir = resolve_path(cfg["paths"]["figures_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    test_samples = _samples(manifest["dataset_A"]["splits"]["test"])
    results = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["seed"],
        "device": device,
        "dataset": "A/test",
        "n_test": len(test_samples),
        "models": {},
    }

    for name, meta in cfg["checkpoints"].items():
        if not meta.get("enabled", True):
            continue
        ckpt = resolve_path(meta["path"])
        if not ckpt.exists():
            results["models"][name] = {"status": "missing_checkpoint", "path": str(ckpt)}
            continue
        try:
            model, load_info = load_checkpoint_model(ckpt, device)
            batch = run_inference(
                model,
                test_samples,
                device=device,
                image_size=int(cfg["image_size"]),
                batch_size=int(cfg["batch_size"]),
            )
            metrics = binary_metrics(batch.labels, batch.probs, threshold=float(cfg["threshold"]))
            ece = expected_calibration_error(batch.labels, batch.probs, n_bins=int(cfg["calibration"]["n_bins"]))
            per_image = float(batch.inference_seconds / max(len(batch.paths), 1))
            model_out = {
                "status": "ok",
                "checkpoint": str(ckpt),
                "load_info": load_info,
                "metrics": metrics,
                "ece_uncalibrated": ece,
                "inference_seconds_total": batch.inference_seconds,
                "inference_seconds_per_image": per_image,
                "predictions": {
                    "paths": batch.paths,
                    "labels": batch.labels.tolist(),
                    "fake_probabilities": batch.probs.tolist(),
                    "logits": batch.logits.tolist(),
                },
            }
            results["models"][name] = model_out

            # confusion matrix figure
            try:
                import matplotlib.pyplot as plt
                import seaborn as sns
                from sklearn.metrics import confusion_matrix

                cm = confusion_matrix(batch.labels, (batch.probs >= cfg["threshold"]).astype(int), labels=[0, 1])
                plt.figure(figsize=(5, 4))
                sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                            xticklabels=["Real", "Fake"], yticklabels=["Real", "Fake"])
                plt.title(f"Confusion — {name} (A/test)")
                plt.ylabel("True")
                plt.xlabel("Predicted")
                plt.tight_layout()
                fig_path = fig_dir / f"confusion_{name}.png"
                plt.savefig(fig_path, dpi=120)
                plt.close()
                model_out["confusion_figure"] = str(fig_path)
            except Exception as e:
                model_out["confusion_figure_error"] = str(e)

            # Persist per-model predictions separately for calibration/ablation
            save_json(out_dir / f"predictions_{name}.json", {
                "model": name,
                "split": "A/test",
                "paths": batch.paths,
                "labels": batch.labels.tolist(),
                "fake_probabilities": batch.probs.tolist(),
                "logits": batch.logits.tolist(),
            })
            print(f"[OK] {name}: acc={metrics['accuracy']:.4f} f1={metrics['f1']:.4f} "
                  f"auc={metrics['roc_auc']} time/img={per_image*1000:.1f}ms")
        except Exception as e:
            results["models"][name] = {"status": "failed", "error": str(e), "path": str(ckpt)}
            print(f"[FAIL] {name}: {e}")

    # Drop bulky predictions from summary metrics file
    summary = {
        **{k: v for k, v in results.items() if k != "models"},
        "models": {
            k: {kk: vv for kk, vv in v.items() if kk != "predictions"}
            for k, v in results["models"].items()
        },
    }
    save_json(out_dir / "metrics.json", summary)
    save_json(out_dir / "metrics_full.json", results)
    print(f"Wrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
