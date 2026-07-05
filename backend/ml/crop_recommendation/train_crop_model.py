"""
Train RandomForest crop recommendation model.

IMPORTANT: This script ships with a synthetic dataset generator so you get a
WORKING model immediately. For real-world accuracy, replace `load_dataset()`
with the actual Kaggle "Crop_recommendation.csv" dataset:
https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

Just drop the CSV in this folder as Crop_recommendation.csv and this script
will auto-detect and use it instead of synthetic data.
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "Crop_recommendation.csv")

# Approximate ideal growing conditions per crop (mean, std) for
# N, P, K, temperature, humidity, ph, rainfall
CROP_PROFILES = {
    "rice":        {"N": (80, 15), "P": (45, 10), "K": (40, 10), "temperature": (25, 3), "humidity": (82, 5), "ph": (6.2, 0.5), "rainfall": (220, 40)},
    "maize":       {"N": (80, 15), "P": (45, 10), "K": (20, 8),  "temperature": (24, 4), "humidity": (60, 10), "ph": (6.3, 0.5), "rainfall": (85, 25)},
    "chickpea":    {"N": (40, 10), "P": (65, 10), "K": (80, 10), "temperature": (19, 3), "humidity": (17, 5), "ph": (7.3, 0.5), "rainfall": (80, 20)},
    "kidneybeans": {"N": (20, 8),  "P": (65, 10), "K": (20, 8),  "temperature": (18, 3), "humidity": (21, 5), "ph": (5.8, 0.4), "rainfall": (105, 25)},
    "pigeonpeas":  {"N": (20, 8),  "P": (65, 10), "K": (20, 8),  "temperature": (27, 4), "humidity": (48, 10), "ph": (5.8, 0.5), "rainfall": (150, 30)},
    "mothbeans":   {"N": (20, 8),  "P": (48, 10), "K": (20, 8),  "temperature": (28, 3), "humidity": (53, 10), "ph": (6.8, 0.5), "rainfall": (52, 15)},
    "mungbean":    {"N": (20, 8),  "P": (47, 10), "K": (20, 8),  "temperature": (28, 3), "humidity": (85, 5), "ph": (6.7, 0.4), "rainfall": (50, 15)},
    "blackgram":   {"N": (40, 10), "P": (67, 10), "K": (19, 8),  "temperature": (29, 3), "humidity": (65, 10), "ph": (7.1, 0.5), "rainfall": (68, 15)},
    "lentil":      {"N": (18, 8),  "P": (68, 10), "K": (19, 8),  "temperature": (24, 3), "humidity": (65, 10), "ph": (6.9, 0.5), "rainfall": (46, 15)},
    "pomegranate": {"N": (18, 8),  "P": (18, 8),  "K": (40, 10), "temperature": (21, 3), "humidity": (90, 5), "ph": (6.4, 0.5), "rainfall": (108, 20)},
    "banana":      {"N": (100, 15),"P": (82, 10), "K": (50, 10), "temperature": (27, 3), "humidity": (80, 5), "ph": (5.9, 0.4), "rainfall": (105, 25)},
    "mango":       {"N": (20, 8),  "P": (27, 8),  "K": (30, 8),  "temperature": (32, 3), "humidity": (50, 10), "ph": (5.7, 0.4), "rainfall": (95, 20)},
    "grapes":      {"N": (18, 8),  "P": (125, 15),"K": (200, 20),"temperature": (24, 3), "humidity": (82, 5), "ph": (6.0, 0.4), "rainfall": (70, 15)},
    "watermelon":  {"N": (100, 15),"P": (17, 8),  "K": (50, 10), "temperature": (25, 3), "humidity": (85, 5), "ph": (6.5, 0.4), "rainfall": (50, 15)},
    "muskmelon":   {"N": (100, 15),"P": (17, 8),  "K": (50, 10), "temperature": (28, 3), "humidity": (92, 5), "ph": (6.3, 0.4), "rainfall": (25, 10)},
    "apple":       {"N": (20, 8),  "P": (135, 15),"K": (200, 20),"temperature": (22, 3), "humidity": (92, 5), "ph": (5.9, 0.4), "rainfall": (110, 20)},
    "orange":      {"N": (19, 8),  "P": (16, 8),  "K": (10, 5),  "temperature": (22, 3), "humidity": (92, 5), "ph": (7.0, 0.4), "rainfall": (110, 20)},
    "papaya":      {"N": (50, 10), "P": (59, 10), "K": (50, 10), "temperature": (33, 3), "humidity": (92, 5), "ph": (6.7, 0.4), "rainfall": (145, 25)},
    "coconut":     {"N": (21, 8),  "P": (16, 8),  "K": (30, 8),  "temperature": (27, 3), "humidity": (94, 5), "ph": (5.9, 0.4), "rainfall": (175, 30)},
    "cotton":      {"N": (117, 15),"P": (46, 10), "K": (19, 8),  "temperature": (24, 3), "humidity": (80, 5), "ph": (6.9, 0.5), "rainfall": (80, 20)},
    "jute":        {"N": (78, 15), "P": (47, 10), "K": (40, 10), "temperature": (25, 3), "humidity": (80, 5), "ph": (6.7, 0.4), "rainfall": (175, 30)},
    "coffee":      {"N": (100, 15),"P": (18, 8),  "K": (30, 8),  "temperature": (25, 3), "humidity": (58, 10), "ph": (6.8, 0.4), "rainfall": (155, 25)},
}


def generate_synthetic_dataset(samples_per_crop=150, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for crop, profile in CROP_PROFILES.items():
        for _ in range(samples_per_crop):
            row = {}
            for feature, (mean, std) in profile.items():
                val = rng.normal(mean, std)
                row[feature] = max(val, 0)
            row["label"] = crop
            rows.append(row)
    df = pd.DataFrame(rows)
    return df


def load_dataset():
    if os.path.exists(CSV_PATH):
        print(f"Using real dataset found at {CSV_PATH}")
        return pd.read_csv(CSV_PATH)
    print("No Crop_recommendation.csv found - generating synthetic dataset "
          "(replace with the real Kaggle dataset for production accuracy).")
    return generate_synthetic_dataset()


def train():
    df = load_dataset()
    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

    X = df[feature_cols]
    y = df["label"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.4f}")
    print(classification_report(y_test, preds, target_names=le.classes_))

    joblib.dump(model, os.path.join(HERE, "crop_model.pkl"))
    joblib.dump(scaler, os.path.join(HERE, "scaler.pkl"))
    joblib.dump(le, os.path.join(HERE, "label_encoder.pkl"))
    joblib.dump(feature_cols, os.path.join(HERE, "feature_cols.pkl"))
    print("Saved crop_model.pkl, scaler.pkl, label_encoder.pkl, feature_cols.pkl")


if __name__ == "__main__":
    train()
