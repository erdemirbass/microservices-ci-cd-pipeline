#!/usr/bin/env python3
"""
Apply a list of Kubernetes manifest files or directories if they exist.

Usage:
    python ops/k8s/apply_manifests.py <path> [<path> ...]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def kubectl_apply(path: Path) -> None:
    print(f"Applying manifests from {path}")
    subprocess.run(["kubectl", "apply", "-f", str(path)], check=True)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python ops/k8s/apply_manifests.py <path> [<path> ...]", file=sys.stderr)
        sys.exit(1)

    for raw in sys.argv[1:]:
        path = Path(raw)
        if not path.exists():
            print(f"Skipping {path}: not found")
            continue
        kubectl_apply(path)


if __name__ == "__main__":
    main()
