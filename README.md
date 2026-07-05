# 🌾 AI-Based Farmer Query Support System

Full-stack farmer advisory app: crop recommendation (RandomForest), plant disease
detection (ResNet50 transfer learning), an AI chatbot (Gemini + govt schemes),
and live weather.

```
agri-ai/
├── backend/                  # Flask API
│   ├── app.py                 # app factory
│   ├── run.py                 # entrypoint (gunicorn target)
│   ├── config.py
│   ├── extensions.py
│   ├── models/                 # SQLAlchemy models (User, history tables)
│   ├── routes/                 # auth, crop, disease, chat, weather blueprints
│   ├── services/                # business logic + ML inference
│   ├── ml/
│   │   ├── crop_recommendation/  # trained RF model already included ✅
│   │   └── disease_detection/    # train this yourself (see its README.md)
│   ├── data/                   # govt_schemes.json, disease_info.json
│   ├── requirements.txt
│   ├── Dockerfile / Procfile
│   └── .env.example
└── frontend/                  # static HTML/CSS/JS (no build step needed)
    ├── index.html
    ├── config.js               # <- EDIT API_URL here after deploying backend
    ├── pages/                   # login, register, dashboard, crop, disease, chat, weather
    ├── assets/{css,js}/
    └── translations/            # en.json, hi.json, ...
```

## 1. Local setup (test before deploying)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: add GEMINI_API_KEY and OPENWEATHER_API_KEY
python run.py
```
Backend runs at `http://localhost:5000`. Check `http://localhost:5000/api/health`.

Crop model is **already trained and included** (`ml/crop_recommendation/*.pkl`,
trained on the real Kaggle Crop_recommendation.csv you gave me — 99.3% test accuracy).

Disease model needs one training run on your side (10-15 min, no GPU) — follow
`backend/ml/disease_detection/README.md` (uses the `emmarex/plantdisease`
dataset you already downloaded via kagglehub).

### Frontend
Just open `frontend/index.html` in a browser, OR serve it with any static server:
```bash
cd frontend
python -m http.server 8080
```
Visit `http://localhost:8080`. Before that, make sure `frontend/config.js` →
`API_URL` points to your backend (`http://localhost:5000` for local testing).

## 2. Deploy today (Render — same as your SHL project)

### Backend → Render Web Service
1. Push this whole repo to GitHub.
2. Render → New → Web Service → connect repo → set **Root Directory: `backend`**.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 run:app`
5. Add environment variables (from your `.env`):
   - `SECRET_KEY`, `JWT_SECRET_KEY` (any long random strings)
   - `GEMINI_API_KEY` (from https://aistudio.google.com/app/apikey)
   - `OPENWEATHER_API_KEY` (from https://openweathermap.org/api)
   - `DATABASE_URL` → leave default (SQLite) for a quick demo, or attach a
     Render Postgres instance later for persistence across restarts
   - `CORS_ORIGINS` → set to your frontend's Render URL once you have it
6. Deploy. Note the backend URL, e.g. `https://agri-ai-backend.onrender.com`.

⚠️ Render free tier's disk is **ephemeral** — if you don't train+commit the
disease model files before deploying, `/api/disease/detect` will return a clear
"model not trained yet" error instead of crashing (by design). Train locally
first, then commit the 3 generated files in `ml/disease_detection/` before pushing.

### Frontend → Render Static Site
1. Render → New → Static Site → same repo → **Root Directory: `frontend`**.
2. Build Command: leave empty. Publish Directory: `.`
3. Before deploying (or after, then redeploy), edit `frontend/config.js`:
   ```js
   API_URL: (window.__AGRI_API_URL__ || "https://agri-ai-backend.onrender.com"),
   ```
   (replace with your actual backend URL from the step above)
4. Deploy. You'll get something like `https://agri-ai-frontend.onrender.com`.
5. Go back to the backend's `CORS_ORIGINS` env var and set it to this frontend URL,
   then redeploy the backend.

That's it — both live, same pattern as your SHL Render deployment.

## 3. API endpoints quick reference

| Feature | Method | Endpoint |
|---|---|---|
| Register | POST | `/api/auth/register` |
| Login | POST | `/api/auth/login` |
| Crop recommend | POST | `/api/crop/recommend` (auth) |
| Crop history | GET | `/api/crop/history` (auth) |
| Disease detect | POST | `/api/disease/detect` (auth, multipart `image` + `crop_name`) |
| Disease history | GET | `/api/disease/history` (auth) |
| Chat | POST | `/api/chat/chat` (body: `user_id`, `message`, `lang`) |
| Weather current | GET | `/api/weather/current?city=` or `?lat=&lon=` (auth) |
| Weather forecast | GET | `/api/weather/forecast?city=` (auth) |
| Health check | GET | `/api/health` |

## 4. Retraining models

- **Crop model**: `python backend/ml/crop_recommendation/train_crop_model.py`
  (already uses your real Kaggle CSV, sitting in that folder)
- **Disease model**: see `backend/ml/disease_detection/README.md`



#frontend == cd "C:\Users\Bhumi Bhardwaj\Downloads\agri-ai-project\agri-ai\frontend"
python -m http.server 8080
http://localhost:8080

#backend == cd agri-ai\backend
venv\Scripts\activate
python run.py
