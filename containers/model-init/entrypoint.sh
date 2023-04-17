#!/bin/bash
if [ -z "$MODEL_URL" ]; then
    exit 1
fi
MODEL_PATH="${MODEL_PATH:-/opt/ml}"
if [ ! -d "${MODEL_PATH}" ]; then
    mkdir -p "${MODEL_PATH}"
fi
curl -s -L "${MODEL_URL}" | tar xv -C "${MODEL_PATH}" --no-same-owner
