import os
import joblib
import numpy as np
import pandas as pd
from flask import current_app


class CropService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_cols = None
        self._loaded = False

    def load(self, model_dir):
        model_path = os.path.join(model_dir, "crop_model.pkl")
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        encoder_path = os.path.join(model_dir, "label_encoder.pkl")
        cols_path = os.path.join(model_dir, "feature_cols.pkl")

        if not all(os.path.exists(p) for p in [model_path, scaler_path, encoder_path, cols_path]):
            print(f"[CropService] Model files not found in {model_dir}. "
                  f"Run ml/crop_recommendation/train_crop_model.py first.")
            return

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.label_encoder = joblib.load(encoder_path)
        self.feature_cols = joblib.load(cols_path)
        self._loaded = True
        print("[CropService] Crop recommendation model loaded.")

    def is_ready(self):
        return self._loaded

    def predict(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, top_k=3):
        if not self._loaded:
            raise RuntimeError("Crop model not loaded. Train it first (see ml/crop_recommendation/).")

        X = pd.DataFrame(
            [[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]],
            columns=self.feature_cols,
        )
        X_scaled = self.scaler.transform(X)

        probs = self.model.predict_proba(X_scaled)[0]
        top_indices = np.argsort(probs)[::-1][:top_k]

        recommendations = []
        for idx in top_indices:
            crop_name = self.label_encoder.inverse_transform([idx])[0]
            recommendations.append({
                "crop": crop_name.capitalize(),
                "confidence": round(float(probs[idx]) * 100, 2),
            })
        return recommendations


crop_service = CropService()


def init_crop_service(app):
    with app.app_context():
        crop_service.load(current_app.config["CROP_MODEL_DIR"])
