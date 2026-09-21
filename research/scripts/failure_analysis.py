#!/usr/bin/env python3
"""Failure analysis on real evaluation predictions (counts, rates, examples)."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from _lib import load_config, resolve_path, save_json, set_seed


def categorize(y_true: int, y_prob: float, threshold: float = 0.5) -> str:
    y_pred = 1 if y_prob >= threshold else 0
    if y_true == 1 and y_pred == 1:
        return "true_positive"
    if y_true == 0 and y_pred == 0:
        return "true_negative"
    if y_true == 0 and y_pred == 1:
        return "false_positive"
    return "false_negative"


def main() -> None:
    cfg = load_config()
    set_seed(int(cfg["seed"]))
    pred_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "evaluation"
    out_dir = resolve_path(cfg["paths"]["outputs_dir"]) / "failure_analysis"
    examples_dir = out_dir / "examples"
    out_dir.mkdir(parents=True, exist_ok=True)
    examples_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["seed"],
        "threshold": cfg["threshold"],
        "models": {},
    }

    for pred_file in sorted(pred_dir.glob("predictions_*.json")):
        with open(pred_file, encoding="utf-8") as f:
            data = json.load(f)
        name = data["model"]
        labels = np.asarray(data["labels"], dtype=int)
        probs = np.asarray(data["fake_probabilities"], dtype=float)
        paths = data["paths"]

        cats = [categorize(int(y), float(p), cfg["threshold"]) for y, p in zip(labels, probs)]
        counts = {k: cats.count(k) for k in ("true_positive", "true_negative", "false_positive", "false_negative")}
        n = len(cats)
        rates = {k: (v / n if n else 0.0) for k, v in counts.items()}

        # High-confidence errors
        fp_idx = [i for i, c in enumerate(cats) if c == "false_positive"]
        fn_idx = [i for i, c in enumerate(cats) if c == "false_negative"]
        fp_idx.sort(key=lambda i: probs[i], reverse=True)
        fn_idx.sort(key=lambda i: probs[i])  # most confidently wrong as real

        def take(idxs, k=8):
            out = []
            for i in idxs[:k]:
                src = Path(paths[i])
                dst_name = f"{name}_{categorize(int(labels[i]), float(probs[i]), cfg['threshold'])}_{i}_{src.name}"
                dst = examples_dir / dst_name
                try:
                    shutil.copy2(src, dst)
                    copied = str(dst)
                except Exception:
                    copied = None
                out.append({
                    "path": paths[i],
                    "copied_to": copied,
                    "label": int(labels[i]),
                    "fake_probability": float(probs[i]),
                    "category": cats[i],
                })
            return out

        report["models"][name] = {
            "n": n,
            "counts": counts,
            "rates": rates,
            "false_positive_rate": rates["false_positive"],
            "false_negative_rate": rates["false_negative"],
            "representative_false_positives": take(fp_idx),
            "representative_false_negatives": take(fn_idx),
        }
        print(
            f"[OK] {name}: FP={counts['false_positive']} ({rates['false_positive']:.3f}) "
            f"FN={counts['false_negative']} ({rates['false_negative']:.3f})"
        )

    save_json(out_dir / "failure_report.json", report)
    print(f"Wrote {out_dir / 'failure_report.json'}")


if __name__ == "__main__":
    main()
