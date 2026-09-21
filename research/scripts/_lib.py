"""Shared helpers for research evaluation (deterministic, traceable)."""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    path = config_path or (REPO_ROOT / "research" / "configs" / "eval_config.yaml")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_config_path"] = str(path)
    return cfg


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass


def ensure_repo_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    backend = REPO_ROOT / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    app = REPO_ROOT / "backend" / "app"
    if str(app) not in sys.path:
        sys.path.insert(0, str(app))


def resolve_path(rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else (REPO_ROOT / p)


def file_sha256(path: Path, max_bytes: int = 2_000_000) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        remaining = max_bytes
        while remaining > 0:
            chunk = f.read(min(65536, remaining))
            if not chunk:
                break
            h.update(chunk)
            remaining -= len(chunk)
    return h.hexdigest()


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_labeled_images(root: Path, real_dir: str, fake_dir: str) -> List[Tuple[str, int]]:
    samples: List[Tuple[str, int]] = []
    for label, sub in ((0, real_dir), (1, fake_dir)):
        d = root / sub
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                samples.append((str(p.resolve()), label))
    return samples


def stratified_split(
    samples: List[Tuple[str, int]],
    fractions: Dict[str, float],
    seed: int,
    max_per_split: Optional[Dict[str, Optional[int]]] = None,
) -> Dict[str, List[Tuple[str, int]]]:
    """Deterministic stratified split. fractions keys e.g. train/calibration/test."""
    rng = random.Random(seed)
    by_label: Dict[int, List[Tuple[str, int]]] = {0: [], 1: []}
    for s in samples:
        by_label[int(s[1])].append(s)
    for lab in by_label:
        by_label[lab].sort(key=lambda x: x[0])
        rng.shuffle(by_label[lab])

    names = list(fractions.keys())
    out: Dict[str, List[Tuple[str, int]]] = {n: [] for n in names}
    for lab, items in by_label.items():
        n = len(items)
        idx = 0
        allocated = 0
        for i, name in enumerate(names):
            if i == len(names) - 1:
                chunk = items[idx:]
            else:
                k = int(round(fractions[name] * n))
                chunk = items[idx : idx + k]
                idx += k
            out[name].extend(chunk)
            allocated += len(chunk)

    for name in names:
        out[name].sort(key=lambda x: x[0])
        if max_per_split and max_per_split.get(name):
            cap = int(max_per_split[name])
            # stratified subsample
            rng2 = random.Random(seed + hash(name) % 10_000)
            real = [s for s in out[name] if s[1] == 0]
            fake = [s for s in out[name] if s[1] == 1]
            rng2.shuffle(real)
            rng2.shuffle(fake)
            n_real = min(len(real), cap // 2)
            n_fake = min(len(fake), cap - n_real)
            chosen = real[:n_real] + fake[:n_fake]
            chosen.sort(key=lambda x: x[0])
            out[name] = chosen
    return out


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=_json_default)


def _json_default(o: Any):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(type(o))


def binary_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
        confusion_matrix,
    )

    y_true = np.asarray(y_true).astype(int)
    y_prob = np.clip(np.asarray(y_prob).astype(float), 0.0, 1.0)
    y_pred = (y_prob >= threshold).astype(int)

    metrics: Dict[str, Any] = {
        "n": int(len(y_true)),
        "n_real": int((y_true == 0).sum()),
        "n_fake": int((y_true == 1).sum()),
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }
    # ROC-AUC only if both classes present
    if len(np.unique(y_true)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
    else:
        metrics["roc_auc"] = None
    return metrics


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 15,
) -> Dict[str, Any]:
    """
    ECE for binary fake-probability: bins by P(fake), compares mean P to fraction fake.
    Also computes confidence-ECE using max(p, 1-p) vs correctness.
    """
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.clip(np.asarray(y_prob).astype(float), 0.0, 1.0)

    def _ece_prob() -> Tuple[float, List[Dict[str, float]]]:
        edges = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        bins = []
        for i in range(n_bins):
            lo, hi = edges[i], edges[i + 1]
            if i == n_bins - 1:
                mask = (y_prob >= lo) & (y_prob <= hi)
            else:
                mask = (y_prob >= lo) & (y_prob < hi)
            if not np.any(mask):
                continue
            conf = float(y_prob[mask].mean())
            acc = float(y_true[mask].mean())  # fraction fake
            w = float(mask.mean())
            ece += w * abs(conf - acc)
            bins.append({"lo": float(lo), "hi": float(hi), "count": int(mask.sum()),
                         "avg_prob": conf, "frac_positive": acc, "gap": abs(conf - acc)})
        return float(ece), bins

    conf = np.maximum(y_prob, 1.0 - y_prob)
    pred = (y_prob >= 0.5).astype(int)
    correct = (pred == y_true).astype(float)

    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece_conf = 0.0
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        mask = (conf >= lo) & (conf < hi) if i < n_bins - 1 else (conf >= lo) & (conf <= hi)
        if not np.any(mask):
            continue
        ece_conf += float(mask.mean()) * abs(float(conf[mask].mean()) - float(correct[mask].mean()))

    ece_p, bins = _ece_prob()
    return {
        "ece_probability": ece_p,
        "ece_confidence": float(ece_conf),
        "n_bins": n_bins,
        "reliability_bins": bins,
    }


@dataclass
class EvalBatchResult:
    paths: List[str]
    labels: np.ndarray
    probs: np.ndarray
    logits: np.ndarray
    inference_seconds: float


def build_efficientnet(pretrained: bool = False):
    import torch.nn as nn
    from torchvision.models import efficientnet_b0

    class EfficientNetDeepfake(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = efficientnet_b0(weights=None)
            num_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.BatchNorm1d(512),
                nn.Dropout(0.2),
                nn.Linear(512, 128),
                nn.ReLU(),
                nn.BatchNorm1d(128),
                nn.Dropout(0.1),
                nn.Linear(128, 1),
            )

        def forward(self, x):
            return self.backbone(x)

    return EfficientNetDeepfake()


def load_checkpoint_model(ckpt_path: Path, device: str):
    import torch

    model = build_efficientnet(pretrained=False)
    state = torch.load(str(ckpt_path), map_location="cpu")
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]
    # strip module. prefix if present
    if isinstance(state, dict):
        cleaned = {}
        for k, v in state.items():
            nk = k[7:] if k.startswith("module.") else k
            cleaned[nk] = v
        missing, unexpected = model.load_state_dict(cleaned, strict=False)
    else:
        raise ValueError(f"Unrecognized checkpoint format: {ckpt_path}")
    model.to(device)
    model.eval()
    return model, {
        "missing_keys": list(missing),
        "unexpected_keys": list(unexpected),
        "n_missing": len(missing),
        "n_unexpected": len(unexpected),
    }


def run_inference(
    model,
    samples: Sequence[Tuple[str, int]],
    device: str,
    image_size: int = 224,
    batch_size: int = 32,
) -> EvalBatchResult:
    import cv2
    import torch
    from torchvision import transforms

    tfm = transforms.Compose(
        [
            transforms.ToPILImage(),
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    paths: List[str] = []
    labels: List[int] = []
    probs: List[float] = []
    logits: List[float] = []

    t0 = time.perf_counter()
    with torch.no_grad():
        for i in range(0, len(samples), batch_size):
            batch = samples[i : i + batch_size]
            tensors = []
            batch_labels = []
            batch_paths = []
            for path, lab in batch:
                img = cv2.imread(path)
                if img is None:
                    continue
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                tensors.append(tfm(img))
                batch_labels.append(int(lab))
                batch_paths.append(path)
            if not tensors:
                continue
            x = torch.stack(tensors).to(device)
            out = model(x).squeeze(-1)
            if out.ndim == 0:
                out = out.unsqueeze(0)
            prob = torch.sigmoid(out).detach().cpu().numpy()
            logit = out.detach().cpu().numpy()
            for j in range(len(batch_paths)):
                paths.append(batch_paths[j])
                labels.append(batch_labels[j])
                probs.append(float(prob[j]))
                logits.append(float(logit[j]))
    elapsed = time.perf_counter() - t0
    return EvalBatchResult(
        paths=paths,
        labels=np.asarray(labels, dtype=int),
        probs=np.asarray(probs, dtype=float),
        logits=np.asarray(logits, dtype=float),
        inference_seconds=float(elapsed),
    )


def fit_temperature(logits: np.ndarray, labels: np.ndarray, init: float = 1.0, lr: float = 0.01, steps: int = 200) -> float:
    """NLL temperature scaling on logits for binary BCE-with-logits."""
    import torch
    import torch.nn as nn

    z = torch.tensor(logits, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32)
    log_t = torch.nn.Parameter(torch.tensor([np.log(max(init, 1e-3))], dtype=torch.float32))
    opt = torch.optim.LBFGS([log_t], lr=lr, max_iter=steps)

    criterion = nn.BCEWithLogitsLoss()

    def closure():
        opt.zero_grad()
        t = torch.exp(log_t)
        loss = criterion(z / t, y)
        loss.backward()
        return loss

    opt.step(closure)
    return float(torch.exp(log_t).detach().item())


def apply_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    import torch

    z = torch.tensor(logits, dtype=torch.float32)
    return torch.sigmoid(z / max(temperature, 1e-6)).numpy()
