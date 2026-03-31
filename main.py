from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
from pathlib import Path

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_path = Path("model/ids.pkl")
if not model_path.exists():
    raise FileNotFoundError("Model not found. Run: python -m model.train")

model_data = joblib.load(model_path)
model = model_data["model"]
encoders = model_data["encoders"]

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/predict")
def predict(data: dict):
    try:
        df = pd.DataFrame([data])
        
        # Encode categorical columns using saved encoders
        for col, encoder in encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col])

        probs = model.predict_proba(df)[0]
        pred = model.predict(df)[0]

        confidence = max(probs)

        # risk score
        risk_score = int(confidence*100)

        # alert logic
        if confidence < 0.75:
            alert = "⚠ Suspicious Traffic"
        elif pred == "anomaly":
            alert = "🚨 Attack Detected"
        else:
            alert = "✅ Normal Traffic"

        return {
            "prediction":str(pred),
            "confidence":confidence,
            "risk_score":risk_score,
            "alert":alert
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))