from __future__ import annotations

import os
import sys
from pathlib import Path

import joblib
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from model.feature_extractor import extract_url_features, is_probably_valid_url, normalize_url

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "development-secret-key")
CORS(app)

MODEL_PATH = (Path(__file__).resolve().parent / os.getenv("MODEL_PATH", "../model/model.pkl")).resolve()
VECTORIZER_PATH = (Path(__file__).resolve().parent / os.getenv("VECTORIZER_PATH", "../model/vectorizer.pkl")).resolve()

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


@app.get("/")
def healthcheck():
    return jsonify({"message": "Phishing detection API is running."})


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    raw_url = str(payload.get("url", "")).strip()

    if not raw_url or not is_probably_valid_url(raw_url):
        return jsonify({"error": "A valid URL is required."}), 400

    normalized_url = normalize_url(raw_url)
    feature_map = extract_url_features(normalized_url)
    transformed = vectorizer.transform([feature_map])
    prediction = int(model.predict(transformed)[0])
    probabilities = model.predict_proba(transformed)[0]
    confidence = float(max(probabilities))

    return jsonify(
        {
            "result": "phishing" if prediction == 1 else "safe",
            "confidence": round(confidence, 4),
            "normalized_url": normalized_url,
        }
    )


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Something went wrong on the server."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
