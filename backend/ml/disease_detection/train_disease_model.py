"""
Train a LIGHTWEIGHT plant disease classifier using ResNet50 transfer learning.

Approach (kept deliberately simple + CPU friendly, NO GPU needed):
  1. Load ResNet50 pretrained on ImageNet, WITHOUT its top layer, and FREEZE it.
     It is used purely as a feature extractor (image -> 2048-length vector).
  2. Run every training image through it ONCE to get its feature vector
     (this is just a forward pass - fast, no backpropagation through ResNet50).
  3. Train a small Dense classifier head on those cached feature vectors.
     Since the head is tiny (2048 -> 256 -> num_classes), training takes only
     a minute or two even on a laptop CPU.

This is a completely standard and valid transfer-learning technique, just the
CPU/laptop-friendly version of it (fine-tuning the full ResNet50 needs a GPU
and hours; this needs neither).

HOW TO RUN (after `import kagglehub; path = kagglehub.dataset_download("emmarex/plantdisease")`):

    python train_disease_model.py --data_dir /path/to/PlantVillage --max_per_class 300

Dataset must be organised as:
    <data_dir>/<ClassName1>/img1.jpg, img2.jpg, ...
    <data_dir>/<ClassName2>/img1.jpg, ...
(this is exactly how the "emmarex/plantdisease" kagglehub dataset is structured)

Outputs (saved into this folder):
    disease_classifier.keras   - the small trained head
    class_indices.json         - maps index -> class label
    img_size.json              - the input image size used (needed at inference)
"""
import os
import json
import argparse
import random
import numpy as np

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # quiet TF logs

import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_SIZE = 128  # small size = fast + lightweight; ResNet50 accepts any size >= 32x32
BATCH_SIZE = 32


def build_feature_extractor():
    base = ResNet50(weights="imagenet", include_top=False, pooling="avg",
                     input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base.trainable = False  # freeze - this is the key "lightweight" trick
    return base


def list_images(data_dir, max_per_class=300, seed=42):
    rng = random.Random(seed)
    classes = sorted([d for d in os.listdir(data_dir)
                       if os.path.isdir(os.path.join(data_dir, d))])
    filepaths, labels = [], []
    for c in classes:
        class_dir = os.path.join(data_dir, c)
        files = [f for f in os.listdir(class_dir)
                 if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        rng.shuffle(files)
        files = files[:max_per_class]
        for f in files:
            filepaths.append(os.path.join(class_dir, f))
            labels.append(c)
    return filepaths, labels, classes


def extract_features(feature_extractor, filepaths):
    features = []
    n = len(filepaths)
    for i in range(0, n, BATCH_SIZE):
        batch_paths = filepaths[i:i + BATCH_SIZE]
        batch_imgs = []
        for p in batch_paths:
            img = load_img(p, target_size=(IMG_SIZE, IMG_SIZE))
            arr = img_to_array(img)
            batch_imgs.append(arr)
        batch_arr = preprocess_input(np.array(batch_imgs))
        batch_features = feature_extractor.predict(batch_arr, verbose=0)
        features.append(batch_features)
        print(f"  extracted {min(i + BATCH_SIZE, n)}/{n}", end="\r")
    print()
    return np.vstack(features)


def train(data_dir, max_per_class, epochs):
    print(f"Scanning dataset at {data_dir} ...")
    filepaths, labels, classes = list_images(data_dir, max_per_class=max_per_class)
    print(f"Found {len(filepaths)} images across {len(classes)} classes.")

    le = LabelEncoder()
    y = le.fit_transform(labels)

    print("Building frozen ResNet50 feature extractor (ImageNet weights)...")
    feature_extractor = build_feature_extractor()

    print("Extracting features (forward pass only, no training happening here yet)...")
    X = extract_features(feature_extractor, filepaths)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    num_classes = len(classes)
    head = models.Sequential([
        layers.Input(shape=(X.shape[1],)),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax"),
    ])
    head.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    print("Training small classifier head on cached features (fast, CPU is fine)...")
    head.fit(X_train, y_train, validation_data=(X_val, y_val),
              epochs=epochs, batch_size=32, verbose=2)

    head.save(os.path.join(HERE, "disease_classifier.keras"))
    with open(os.path.join(HERE, "class_indices.json"), "w") as f:
        json.dump({str(i): c for i, c in enumerate(le.classes_)}, f, indent=2)
    with open(os.path.join(HERE, "img_size.json"), "w") as f:
        json.dump({"img_size": IMG_SIZE}, f)

    print("Saved disease_classifier.keras, class_indices.json, img_size.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True,
                         help="Path to PlantVillage folder (from kagglehub.dataset_download)")
    parser.add_argument("--max_per_class", type=int, default=300,
                         help="Cap images per class to keep it fast & lightweight. "
                              "Increase (e.g. 800) for better accuracy if you have time.")
    parser.add_argument("--epochs", type=int, default=15)
    args = parser.parse_args()
    train(args.data_dir, args.max_per_class, args.epochs)
