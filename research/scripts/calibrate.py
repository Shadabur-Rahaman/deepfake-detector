#!/usr/bin/env python3
"""Held-out temperature scaling + ECE before/after + reliability diagrams."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np

from _lib import (
    apply_temperature,
    binary_metrics,
    expected_calibration_error,
    fit_temperature,
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
    manifest_path = resolve_path(cfg["paths"]["manifests_dir"]) / "dataset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "calibration"
    fig_dir = resolve_path(cfg["paths"]["figures_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    cal_samples = _samples(manifest["dataset_A"]["splits"]["calibration"])
    test_samples = _samples(manifest["dataset_A"]["splits"]["test"])

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["seed"],
        "device": device,
        "note": "Temperature fitted on A/calibration only; metrics reported on A/test. "
                "Production hybrid inference does NOT consume these fitted temperatures.",
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
            cal = run_inference(model, cal_samples, device, cfg["image_size"], cfg["batch_size"])
            test = run_inference(model, test_samples, device, cfg["image_size"], cfg["batch_size"])

            T = fit_temperature(
                cal.logits,
                cal.labels,
                init=float(cfg["calibration"]["temperature_init"]),
                lr=float(cfg["calibration"]["temperature_lr"]),
                steps=int(cfg["calibration"]["temperature_steps"]),
            )
            probs_before = test.probs
            probs_after = apply_temperature(test.logits, T)

            before = {
                "metrics": binary_metrics(test.labels, probs_before, cfg["threshold"]),
                "ece": expected_calibration_error(test.labels, probs_before, cfg["calibration"]["n_bins"]),
            }
            after = {
                "metrics": binary_metrics(test.labels, probs_after, cfg["threshold"]),
                "ece": expected_calibration_error(test.labels, probs_after, cfg["calibration"]["n_bins"]),
            }

            # Reliability diagram
            try:
                import matplotlib.pyplot as plt

                bins = before["ece"]["reliability_bins"]
                xs = [0.5 * (b["lo"] + b["hi"]) for b in bins]
                ys = [b["frac_positive"] for b in bins]
                cs = [b["avg_prob"] for b in bins]
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.plot([0, 1], [0, 1], "--", color="gray", label="perfect")
                ax.plot(cs, ys, "o-", label="before T")
                bins_a = after["ece"]["reliability_bins"]
                ax.plot(
                    [b["avg_prob"] for b in bins_a],
                    [b["frac_positive"] for b in bins_a],
                    "s-",
                    label="after T",
                )
                ax.set_xlabel("Mean predicted P(fake)")
                ax.set_ylabel("Empirical fraction fake")
                ax.set_title(f"Reliability — {name}")
                ax.legend()
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                fig_path = fig_dir / f"reliability_{name}.png"
                fig.tight_layout()
                fig.savefig(fig_path, dpi=120)
                plt.close(fig)
            except Exception as e:
                fig_path = None
                fig_err = str(e)
            else:
                fig_err = None

            report["models"][name] = {
                "status": "ok",
                "load_info": load_info,
                "temperature": T,
                "n_calibration": len(cal.paths),
                "n_test": len(test.paths),
                "before": before,
                "after": after,
                "reliability_figure": str(fig_path) if fig_path else None,
                "reliability_figure_error": fig_err,
            }
            print(
                f"[OK] {name}: T={T:.4f} "
                f"ECE_prob {before['ece']['ece_probability']:.4f} → {after['ece']['ece_probability']:.4f}"
            )
        except Exception as e:
            report["models"][name] = {"status": "failed", "error": str(e)}
            print(f"[FAIL] {name}: {e}")

    save_json(out_dir / "calibration_report.json", report)
    print(f"Wrote {out_dir / 'calibration_report.json'}")


if __name__ == "__main__":
    main()
