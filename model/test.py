import joblib
import numpy as np
from utils.preprocess import load_data

# ---------- load data ----------
X,_ = load_data("data/Test_data.csv")

# ---------- load model ----------
model = joblib.load("model/ids.pkl")

# ---------- predictions ----------
pred = model.predict(X)
probs = model.predict_proba(X)

# ---------- dynamic threshold function ----------
def dynamic_threshold(probabilities):
    return np.mean(probabilities) + np.std(probabilities)

# calculate threshold from probabilities
threshold = dynamic_threshold(probs)

print("Dynamic Threshold:", threshold)
print("\nPredictions:\n")

# ---------- apply adaptive decision ----------
attack_count = 0
normal_count = 0
suspicious_count = 0

print("\nPredictions:\n")

for i in range(len(pred)):

    confidence = max(probs[i])

    if confidence > threshold:
        label = pred[i]
    else:
        label = "suspicious"

    print(label, confidence)

    # counting logic
    if label == "anomaly":
        attack_count += 1
    elif label == "normal":
        normal_count += 1
    else:
        suspicious_count += 1


# ---------- summary ----------
total = len(pred)

print("\n====== TRAFFIC SUMMARY ======")
print("Total Traffic:", total)
print("Attacks:", attack_count)
print("Suspicious:", suspicious_count)
print("Normal:", normal_count)