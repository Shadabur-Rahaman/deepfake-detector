"""Deterministic visual signals used when a named neural model is unavailable.

These are real image statistics (not random): high-frequency energy, blur,
illumination symmetry, and color entropy. Output is P(fake) in [0, 1].
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import cv2
import numpy as np


def _to_bgr(face) -> np.ndarray:
    arr = np.asarray(face)
    if arr.dtype != np.uint8:
        if arr.max() <= 1.0:
            arr = (arr * 255.0).clip(0, 255).astype(np.uint8)
        else:
            arr = arr.clip(0, 255).astype(np.uint8)
    if arr.ndim == 2:
        return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    if arr.shape[-1] == 4:
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
    return arr


def _fft_high_ratio(gray: np.ndarray) -> float:
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    mag = np.log1p(np.abs(fshift))
    h, w = mag.shape
    cy, cx = h // 2, w // 2
    r = max(8, min(h, w) // 8)
    y, x = np.ogrid[:h, :w]
    low = (y - cy) ** 2 + (x - cx) ** 2 <= r * r
    low_e = float(mag[low].mean()) if low.any() else 0.0
    high_e = float(mag[~low].mean()) if (~low).any() else 0.0
    total = low_e + high_e + 1e-8
    return float(np.clip(high_e / total, 0.0, 1.0))


def score_face(face) -> Dict[str, float]:
    bgr = _to_bgr(face)
    if bgr.size == 0:
        return {"p_fake": 0.5, "blur": 0.0, "hf": 0.5, "asym": 0.0, "entropy": 0.5}
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (224, 224), interpolation=cv2.INTER_AREA)

    blur_raw = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # Very low variance => overly smooth (often generated); very high => noisy encode
    blur_score = float(np.clip(1.0 - (blur_raw / 400.0), 0.0, 1.0))

    hf = _fft_high_ratio(gray)

    left, right = gray[:, :112], np.fliplr(gray[:, 112:])
    asym = float(np.mean(np.abs(left.astype(np.float32) - right.astype(np.float32))) / 255.0)

    hist = cv2.calcHist([gray], [0], None, [32], [0, 256]).flatten()
    p = hist / (hist.sum() + 1e-8)
    entropy = float(-(p * np.log2(p + 1e-8)).sum() / 5.0)
    entropy = float(np.clip(entropy, 0.0, 1.0))

    # Generated faces often: too-smooth (high blur_score), odd HF mix, high left-right mismatch
    p_fake = float(np.clip(0.35 * blur_score + 0.25 * hf + 0.25 * asym + 0.15 * (1.0 - entropy), 0.0, 1.0))
    return {"p_fake": p_fake, "blur": blur_score, "hf": hf, "asym": asym, "entropy": entropy}


def score_faces(faces: Sequence) -> Dict[str, float]:
    if not faces:
        return {"p_fake": 0.5, "n": 0.0}
    parts = [score_face(f) for f in list(faces)[:32]]
    p = float(np.mean([x["p_fake"] for x in parts]))
    return {
        "p_fake": p,
        "n": float(len(parts)),
        "blur": float(np.mean([x["blur"] for x in parts])),
        "hf": float(np.mean([x["hf"] for x in parts])),
        "asym": float(np.mean([x["asym"] for x in parts])),
        "entropy": float(np.mean([x["entropy"] for x in parts])),
    }


def lighting_consistency(faces: Sequence) -> float:
    """0 = consistent lighting, 1 = inconsistent (suspicious)."""
    means = []
    for f in list(faces)[:24]:
        bgr = _to_bgr(f)
        if bgr.size == 0:
            continue
        means.append(float(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).mean()))
    if len(means) < 2:
        return 0.3
    std = float(np.std(means))
    return float(np.clip(std / 40.0, 0.0, 1.0))
