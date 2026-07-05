import os
import json
import numpy as np
from PIL import Image


class DiseaseService: 
    def __init__(self):
        self.feature_extractor = None
        self.classifier = None
        self.class_indices = None
        self.img_size = 128
        self.disease_info = {}
        self._loaded = False

    def load(self, model_dir, disease_info_path):
        classifier_path = os.path.join(model_dir, "disease_classifier.keras")
        classes_path = os.path.join(model_dir, "class_indices.json")
        size_path = os.path.join(model_dir, "img_size.json")

        if os.path.exists(disease_info_path):
            with open(disease_info_path) as f:
                self.disease_info = json.load(f)

        if not (os.path.exists(classifier_path) and os.path.exists(classes_path)):
            print(f"[DiseaseService] Trained model not found in {model_dir}. "
                  f"See ml/disease_detection/README.md to train it (uses kagglehub PlantVillage dataset).")
            return

        # Import TF lazily - keeps app startup fast if disease model isn't trained yet
        import tensorflow as tf
        from tensorflow.keras.applications.resnet50 import ResNet50

        if os.path.exists(size_path):
            with open(size_path) as f:
                self.img_size = json.load(f)["img_size"]

        with open(classes_path) as f:
            self.class_indices = json.load(f)

        self.feature_extractor = ResNet50(
            weights="imagenet", include_top=False, pooling="avg",
            input_shape=(self.img_size, self.img_size, 3),
        )
        self.feature_extractor.trainable = False
        self.classifier = tf.keras.models.load_model(classifier_path)
        self._loaded = True
        print("[DiseaseService] Disease detection model loaded.")

    def is_ready(self):
        return self._loaded

    def _preprocess(self, image_path):
        from tensorflow.keras.applications.resnet50 import preprocess_input
        img = Image.open(image_path).convert("RGB").resize((self.img_size, self.img_size))
        arr = np.array(img, dtype=np.float32)
        arr = preprocess_input(arr)
        return np.expand_dims(arr, axis=0)

    def predict(self, image_path):
        if not self._loaded:
            raise RuntimeError(
                "Disease model not trained yet. See backend/ml/disease_detection/README.md"
            )

        x = self._preprocess(image_path)
        features = self.feature_extractor.predict(x, verbose=0)
        probs = self.classifier.predict(features, verbose=0)[0]

        top_idx = int(np.argmax(probs))
        confidence = round(float(probs[top_idx]) * 100, 2)
        raw_label = self.class_indices[str(top_idx)]

        info = self.disease_info.get(raw_label, self.disease_info.get("_default", {}))
        crop = info.get("crop", raw_label.split("_")[0])
        disease = info.get("disease", raw_label.replace("_", " "))

        return {
            "raw_label": raw_label,
            "crop": crop,
            "disease": disease,
            "confidence": confidence,
            "symptoms": info.get("symptoms", "Not available."),
            "treatment": info.get("treatment", "Consult a local agricultural expert."),
            "prevention": info.get("prevention", "Follow standard crop hygiene practices."),
        }


disease_service = DiseaseService()


def init_disease_service(app):
    with app.app_context():
        info_path = os.path.join(app.root_path, "data", "disease_info.json")
        disease_service.load(app.config["DISEASE_MODEL_DIR"], info_path)
