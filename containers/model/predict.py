#!/usr/bin/env python3
import json
import os
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, request

app = Flask(Path(__file__).stem)
model = joblib.load(os.getenv("MODEL_PATH", "/opt/ml/model.joblib"))


@app.route("/ping")
def ping_fn():
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/invocations", methods=["POST"])
def invocations_fn():
    try:
        data = json.loads(request.data)
    except:
        return json.dumps({"success": False, "reason": "Expected JSON"}), 500, {"ContentType": "application/json"}
    try:
        X = pd.DataFrame([data.values()], columns=data.keys())
        y = model.predict(X)
    except:
        return (
            json.dumps({"success": False, "reason": "Unexpected input data"}),
            500,
            {"ContentType": "application/json"},
        )
    return json.dumps({"success": True, "predicted": int(y[0])}), 200, {"ContentType": "application/json"}
