# Disease Detection Model - Training Instructions

Tu already dataset download kar chuki hai kagglehub se. Ab bas ye steps follow kar
(apne laptop pe ya Colab pe, GPU ki zaroorat NAHI hai):

## 1. Install deps (agar nahi hain)
```bash
pip install tensorflow scikit-learn kagglehub pillow numpy
```

## 2. Download dataset (jo tune already kiya hai)
```python
import kagglehub
path = kagglehub.dataset_download("emmarex/plantdisease")
print(path)
```
Ye path kuch aisa dega: `/root/.cache/kagglehub/datasets/emmarex/plantdisease/versions/1/PlantVillage`
(andar jaake dekh lena exact subfolder name jisme class-folders hain, kabhi kabhi
ek extra nested `PlantVillage` folder hota hai)

## 3. Train (isi folder se run kar)
```bash
python train_disease_model.py --data_dir "<PASTE_PATH_FROM_STEP_2>" --max_per_class 300 --epochs 15
```

- `--max_per_class 300` → har class se max 300 images use karega. Isse training
  10-15 minute mein CPU pe hi ho jayegi. Zyada accuracy chahiye to 600-800 kar dena
  (thoda zyada time lagega, but still no GPU chahiye — kyunki ResNet50 FROZEN hai,
  sirf feature extraction ho raha hai, training sirf ek chhoti Dense head pe hai).

- Training khatam hone ke baad ye 3 files generate hongi isi folder mein:
  - `disease_classifier.keras`
  - `class_indices.json`
  - `img_size.json`

  Ye teeno files backend/ml/disease_detection/ folder mein already honi chahiye
  (deploy karte waqt commit kar dena / upload kar dena).

## 4. Verify
Flask backend automatically inhe load karega jab tu `python run.py` chalayegi.
Agar ye files missing hongi to `/api/disease/detect` endpoint ek clear error dega
("model not trained yet") instead of crashing.

## Why this approach (frozen ResNet50 + small head)
- ResNet50 ka backbone already ImageNet pe train hai — bahut acche general
  image features nikaalta hai.
- Hum use FREEZE kar dete hain (train nahi karte), sirf ek chhota classifier
  (2048 → 256 → num_classes) train karte hain uske upar.
- Isse: (a) training bahut fast hoti hai CPU pe bhi, (b) overfitting kam hota hai
  chhote dataset pe, (c) GPU ki koi zaroorat nahi.
- Yehi cheez "transfer learning" kehlata hai — bas fine-tuning wala heavy version
  nahi, feature-extraction wala light version.

## To improve later
- `--max_per_class` badha dena
- Fine-tune karne ke liye last few ResNet50 layers unfreeze kar sakti hai
  (`base.trainable = True` last 10-20 layers ke liye) — but GPU chahiye hoga phir.
