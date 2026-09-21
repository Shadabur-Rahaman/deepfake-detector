# Research Evaluation (iFake / deepfake-detector)

Reproducible evaluation artifacts generated from **code + local datasets + checkpoints**.

## What is evaluated (genuine)

| Asset | Path | Notes |
|-------|------|--------|
| Dataset A | `processed_faces_optimized/train/{real,fake}` | Primary labeled face crops |
| Dataset B | `processed_faces/train/{real,fake}` | Larger set for distribution-shift probe |
| EfficientNet-B0 | `training_outputs/best_model.pth` | Matches `train.py` `EfficientNetDeepfake` |
| EfficientNet finetuned | `model_weights/deepfake_detector_finetuned.pth` | Same architecture family when loadable |
| Ensemble math | `backend/app/services/confidence_aggregator_2025.py` | Corrected named-weight fake-probability aggregator |

## What is NOT claimed

- README marketing accuracy / 30-FPS numbers
- Production hybrid calibration as validated (utilities exist; final hybrid path does not consume fitted temperature)
- Full Ultra-Ensemble 24-model research benchmark (architectures/checkpoints are heterogeneous)

## Determinism

- Seed: see `configs/eval_config.yaml`
- Splits: stratified by label, written to `manifests/`
- Metrics: written under `outputs/<run_id>/`

## Run

```bash
# from repository root
python research/scripts/run_all.py
```

Or stepwise:

```bash
python research/scripts/build_manifest.py
python research/scripts/evaluate_models.py
python research/scripts/calibrate.py
python research/scripts/ablation.py
python research/scripts/distribution_shift.py
python research/scripts/failure_analysis.py
```

## Tests

```bash
python -m pytest research/tests -v
```
