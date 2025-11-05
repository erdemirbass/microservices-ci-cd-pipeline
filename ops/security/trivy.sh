#!/usr/bin/env sh

set -eu

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <image>" >&2
	exit 1
fi

IMAGE="$1"

docker run --rm -v "${HOME}/.cache/trivy:/root/.cache/trivy" -u "$(id -u):$(id -g)" aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 "$IMAGE"
