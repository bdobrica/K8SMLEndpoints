#!/bin/bash

echo "Starting model download..."

MODEL_PATH="${MODEL_PATH:-/opt/ml}"

if [ -z "$MODEL_URL" ]; then
    echo "MODEL_URL environment variable not set, exiting..."
    exit 1
fi

if [ ! -d "${MODEL_PATH}" ]; then
    mkdir -p "${MODEL_PATH}"
fi

if [ -f "${MODEL_PATH}/.model.lock" ]; then
    while [ -f "${MODEL_PATH}/.model.lock" ]; do
        echo "Waiting for model to be downloaded..."
        sleep 1
    done
    if [ -z "$(ls ${MODEL_PATH})" ]; then
        echo "Model download failed, exiting..."
        exit 1
    fi
    echo "Model already downloaded, skipping..."
else
    if [ ! -f "${MODEL_PATH}" ]; then
        touch "${MODEL_PATH}/.model.lock"
        echo "Downloading model from ${MODEL_URL}..."
        curl -s -L "${MODEL_URL}" | tar xzv -C "${MODEL_PATH}" --no-same-owner
        rm -Rf "${MODEL_PATH}/.model.lock"
        echo "Model downloaded successfully."
    fi
fi