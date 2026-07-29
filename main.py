from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from tensorflow import keras

from utils.preprocess import extract_structural, to_payload_text, to_web_payload_text, cat_cols
from utils.embedding import embed_single
from utils.fusion import fuse_single
from utils.web_rules import check_web_rules

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not Path("model/lstm_extractor.keras").exists() or not Path("model/ids_meta.pkl").exists():
    raise FileNotFoundError("Model not found. Run: python -m model.train")

lstm_model = keras.models.load_model("model/lstm_extractor.keras")
meta       = joblib.load("model/ids_meta.pkl")
rf         = meta["rf"]
encoders   = meta["encoders"]
scaler     = meta["scaler"]

request_log = []

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/log")
def get_log():
    return {"total": len(request_log), "entries": request_log[-50:]}

@app.post("/predict")
def predict(data: dict):
    try:
        # --- Support both flat and nested (web) input formats ---
        if "network_features" in data:
            net     = data["network_features"]
            url     = data.get("url", "")
            payload = data.get("payload", "")
            headers = data.get("headers", {})
        else:
            net     = data
            url     = ""
            payload = ""
            headers = {}

        # --- Stage 1: Rule-based web attack detection (fast path) ---
        rule_result = check_web_rules(url, payload, headers)
        if rule_result["matched"]:
            result = {
                "prediction":  "anomaly",
                "confidence":  1.0,
                "risk_score":  100,
                "alert":       f"🚨 {rule_result['attack_type']} Detected",
                "action":      "🚫 Request Blocked",
                "detection":   "rule-based",
                "attack_type": rule_result["attack_type"],
                "timestamp":   datetime.now().isoformat()
            }
            request_log.append({k: result[k] for k in ["timestamp", "prediction", "confidence", "risk_score"]})
            return result

        # --- Stage 2: ML pipeline for network-level detection ---
        df = pd.DataFrame([net])

        # BERT semantic text — use enriched web text if url/payload present
        if url or payload:
            text = to_web_payload_text(url, payload, headers, net)
        else:
            text = to_payload_text(net)

        semantic = embed_single(text)

        for col, enc in encoders.items():
            if col in df.columns:
                df[col] = enc.transform(df[col])

        structural, _ = extract_structural(df, scaler=scaler)
        structural = structural[0]

        X_lstm        = fuse_single(semantic, structural)
        lstm_features = lstm_model.predict(X_lstm, verbose=0)

        pred_label = rf.predict(lstm_features)[0]
        pred_proba = rf.predict_proba(lstm_features)[0]

        pred       = "anomaly" if pred_label == 1 else "normal"
        confidence = float(max(pred_proba))
        risk_score = int(pred_proba[1] * 100)

        if confidence < 0.75:
            alert = "⚠ Suspicious Traffic"
        elif pred == "anomaly":
            alert = "🚨 Attack Detected"
        else:
            alert = "✅ Normal Traffic"

        result = {
            "prediction":  pred,
            "confidence":  round(confidence, 4),
            "risk_score":  risk_score,
            "alert":       alert,
            "action":      "🚫 Request Blocked" if pred == "anomaly" else "✅ Request Allowed & Logged",
            "detection":   "ml-pipeline",
            "attack_type": "anomaly" if pred == "anomaly" else None,
            "timestamp":   datetime.now().isoformat()
        }

        request_log.append({k: result[k] for k in ["timestamp", "prediction", "confidence", "risk_score"]})
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
