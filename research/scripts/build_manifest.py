#!/usr/bin/env python3
"""Build deterministic dataset manifests for research evaluation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from _lib import (
    REPO_ROOT,
    file_sha256,
    list_labeled_images,
    load_config,
    resolve_path,
    save_json,
    set_seed,
    stratified_split,
)


def main() -> None:
    cfg = load_config()
    set_seed(int(cfg["seed"]))

    manifests_dir = resolve_path(cfg["paths"]["manifests_dir"])
    manifests_dir.mkdir(parents=True, exist_ok=True)

    ds_a = cfg["datasets"]["A"]
    root_a = resolve_path(ds_a["root"])
    samples_a = list_labeled_images(root_a, ds_a["real_dir"], ds_a["fake_dir"])
    if not samples_a:
        raise SystemExit(f"No images found under {root_a}")

    splits = stratified_split(
        samples_a,
        cfg["splits"],
        seed=int(cfg["seed"]),
        max_per_split=cfg.get("max_samples_per_split"),
    )

    # Dataset B: independent stratified subsample for shift testing (not used in fitting)
    ds_b = cfg["datasets"]["B"]
    root_b = resolve_path(ds_b["root"])
    samples_b = list_labeled_images(root_b, ds_b["real_dir"], ds_b["fake_dir"])
    shift_cap = (cfg.get("max_samples_per_split") or {}).get("shift_test")
    shift_split = stratified_split(
        samples_b,
        {"shift_test": 1.0},
        seed=int(cfg["seed"]) + 7,
        max_per_split={"shift_test": shift_cap},
    ) if samples_b else {"shift_test": []}

    ckpt_meta = {}
    for name, meta in cfg["checkpoints"].items():
        p = resolve_path(meta["path"])
        ckpt_meta[name] = {
            **meta,
            "exists": p.exists(),
            "resolved_path": str(p),
            "sha256_prefix": file_sha256(p) if p.exists() else None,
            "size_bytes": p.stat().st_size if p.exists() else None,
        }

    def pack(split_samples):
        return [
            {"path": path, "label": int(label), "label_name": "fake" if label == 1 else "real"}
            for path, label in split_samples
        ]

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["seed"],
        "config_path": cfg["_config_path"],
        "dataset_A": {
            "name": ds_a["name"],
            "root": str(root_a),
            "total_available": len(samples_a),
            "n_real_available": sum(1 for _, y in samples_a if y == 0),
            "n_fake_available": sum(1 for _, y in samples_a if y == 1),
            "splits": {k: {
                "n": len(v),
                "n_real": sum(1 for _, y in v if y == 0),
                "n_fake": sum(1 for _, y in v if y == 1),
                "samples": pack(v),
            } for k, v in splits.items()},
        },
        "dataset_B": {
            "name": ds_b["name"],
            "root": str(root_b),
            "total_available": len(samples_b),
            "n_real_available": sum(1 for _, y in samples_b if y == 0),
            "n_fake_available": sum(1 for _, y in samples_b if y == 1),
            "shift_test": {
                "n": len(shift_split["shift_test"]),
                "n_real": sum(1 for _, y in shift_split["shift_test"] if y == 0),
                "n_fake": sum(1 for _, y in shift_split["shift_test"] if y == 1),
                "samples": pack(shift_split["shift_test"]),
            },
        },
        "checkpoints": ckpt_meta,
        "notes": [
            "Splits are stratified by label with a fixed seed.",
            "max_samples_per_split caps are applied after stratification for tractable local runs.",
            "Dataset B shift_test is never used for temperature fitting.",
        ],
    }

    out = manifests_dir / "dataset_manifest.json"
    save_json(out, manifest)
    # Also write lightweight index without full path lists for quick inspection
    summary = {
        "created_utc": manifest["created_utc"],
        "seed": manifest["seed"],
        "dataset_A_splits": {k: {kk: vv for kk, vv in v.items() if kk != "samples"}
                             for k, v in manifest["dataset_A"]["splits"].items()},
        "dataset_B_shift_test": {k: v for k, v in manifest["dataset_B"]["shift_test"].items() if k != "samples"},
        "checkpoints": {k: {kk: vv for kk, vv in v.items() if kk != "sha256_prefix"}
                        for k, v in ckpt_meta.items()},
    }
    save_json(manifests_dir / "dataset_manifest_summary.json", summary)
    print(f"Wrote {out}")
    print(f"A test n={manifest['dataset_A']['splits']['test']['n']} "
          f"cal n={manifest['dataset_A']['splits']['calibration']['n']}")
    print(f"B shift n={manifest['dataset_B']['shift_test']['n']}")


if __name__ == "__main__":
    main()
