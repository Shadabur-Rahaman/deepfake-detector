"""Smoke tests for research evaluation helpers (no GPU required)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _lib import (  # noqa: E402
    binary_metrics,
    expected_calibration_error,
    stratified_split,
)


def test_stratified_split_deterministic():
    samples = [(f"r{i}.jpg", 0) for i in range(50)] + [(f"f{i}.jpg", 1) for i in range(50)]
    a = stratified_split(samples, {"train": 0.7, "test": 0.3}, seed=42, max_per_split={"train": 40, "test": 20})
    b = stratified_split(samples, {"train": 0.7, "test": 0.3}, seed=42, max_per_split={"train": 40, "test": 20})
    assert a["train"] == b["train"]
    assert a["test"] == b["test"]
    assert len(a["train"]) <= 40
    assert len(a["test"]) <= 20


def test_binary_metrics_and_ece():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.4, 0.6, 0.9])
    m = binary_metrics(y, p, threshold=0.5)
    assert m["accuracy"] == 1.0
    assert m["confusion_matrix"] == [[2, 0], [0, 2]]
    e = expected_calibration_error(y, p, n_bins=4)
    assert 0.0 <= e["ece_probability"] <= 1.0
