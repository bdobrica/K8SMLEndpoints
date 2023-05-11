#!/bin/bash

set -euo pipefail

cd "$(dirname $0)"

find . -name "Dockerfile" -exec dirname {} \; | while read -r dir; do
    img=$(basename "$dir")
    tag="quay.io/bdobrica/ml-operator-tools:$img-latest"
    echo "Building $img out of $dir and tag it as $tag ..."
    podman build -t "$tag" -f "$dir/Dockerfile" "$dir"
    podman push "$tag"
    echo "Done."
done
