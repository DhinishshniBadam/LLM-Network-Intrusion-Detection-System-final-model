import joblib
import sys
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers

from utils.preprocess import load_data, get_encoders, extract_structural, to_payload_text
from utils.embedding import embed_texts
from utils.fusion import fuse

print("[ 1/6 ] Loading data...")
encoders = get_encoders("data/Train_data.csv")
df, y = load_data("data/Train_data.csv", encoders=encoders)

print("[ 2/6 ] Extracting structural features...")
X_struct, scaler = extract_structural(df, fit_scaler=True)

print("[ 3/6 ] Generating BERT semantic embeddings...")
# rebuild raw df for text generation (before encoding)
import pandas as pd
raw_df = pd.read_csv("data/Train_data.csv")
texts = raw_df.apply(to_payload_text, axis=1).tolist()
X_semantic = embed_texts(texts)  # (N, 384)

print("[ 4/6 ] Fusing features...")
X_fused = fuse(X_semantic, X_struct)  # (N, 422)

# reshape for LSTM: (N, 1, 422)
X_lstm_input = X_fused.reshape(X_fused.shape[0], 1, X_fused.shape[1])

X_train, X_val, y_train, y_val = train_test_split(X_lstm_input, y, test_size=0.2, random_state=42)

print("[ 5/6 ] Training LSTM temporal model...")
inputs = layers.Input(shape=(1, X_fused.shape[1]))
x = layers.LSTM(128, return_sequences=False)(inputs)
x = layers.Dropout(0.3)(x)
features = layers.Dense(64, activation="relu")(x)
outputs = layers.Dense(1, activation="sigmoid")(features)

lstm_model = keras.Model(inputs=inputs, outputs=outputs)
feature_extractor = keras.Model(inputs=inputs, outputs=features)

lstm_model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
lstm_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=10,
    batch_size=256,
    verbose=1
)

# extract LSTM features for RF input
print("[ 6/6 ] Training Random Forest classifier...")
X_train_feat = feature_extractor.predict(X_train, verbose=0)
X_val_feat   = feature_extractor.predict(X_val,   verbose=0)

rf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
rf.fit(X_train_feat, y_train)

y_pred = rf.predict(X_val_feat)
print(classification_report(y_val, y_pred, target_names=["normal", "anomaly"]))

# save everything
feature_extractor.save("model/lstm_extractor.keras")
joblib.dump({
    "rf": rf,
    "encoders": encoders,
    "scaler": scaler
}, "model/ids_meta.pkl")

print("✓ Pipeline saved: model/lstm_extractor.keras + model/ids_meta.pkl")
