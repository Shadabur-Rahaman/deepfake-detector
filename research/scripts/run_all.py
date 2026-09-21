#!/usr/bin/env python3
"""Run the full research evaluation pipeline in order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "build_manifest.py",
    "evaluate_models.py",
    "calibrate.py",
    "ablation.py",
    "distribution_shift.py",
    "failure_analysis.py",
]


def main() -> int:
    here = Path(__file__).resolve().parent
    for name in SCRIPTS:
        path = here / name
        print("\n" + "=" * 60)
        print(f"RUNNING {name}")
        print("=" * 60)
        proc = subprocess.run([sys.executable, str(path)], cwd=str(here))
        if proc.returncode != 0:
            print(f"FAILED: {name} (exit {proc.returncode})")
            return proc.returncode
    print("\nAll research stages completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
