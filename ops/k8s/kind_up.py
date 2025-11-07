#!/usr/bin/env python3

"""
Helper script to ensure a kind cluster and Kubernetes namespace exist.

Usage: python ops/k8s/kind_up.py <cluster-name> [namespace]
"""

from __future__ import annotations

import subprocess
import sys
from typing import Iterable


def run(cmd: Iterable[str], *, check: bool = True, capture: bool = False):
    kwargs = {"check": check}
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    return subprocess.run(cmd, **kwargs)


def list_clusters() -> set[str]:
    result = run(["kind", "get", "clusters"], capture=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def ensure_cluster(name: str):
    clusters = list_clusters()
    if name in clusters:
        print(f"kind cluster '{name}' already exists")
        return
    print(f"Creating kind cluster '{name}'")
    run(["kind", "create", "cluster", "--name", name])


def ensure_namespace(namespace: str):
    result = subprocess.run(
        ["kubectl", "get", "namespace", namespace],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        print(f"Namespace '{namespace}' already exists")
        return
    print(f"Creating namespace '{namespace}'")
    run(["kubectl", "create", "namespace", namespace])


def main():
    if len(sys.argv) < 2:
        print("Usage: python ops/k8s/kind_up.py <cluster-name> [namespace]", file=sys.stderr)
        sys.exit(1)
    cluster = sys.argv[1]
    namespace = sys.argv[2] if len(sys.argv) >= 3 else cluster

    ensure_cluster(cluster)
    ensure_namespace(namespace)


if __name__ == "__main__":
    main()
