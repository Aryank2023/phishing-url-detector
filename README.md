# Phishing URL Detection Web App

A production-ready full-stack web application that detects whether a URL is likely phishing or safe using a trained machine learning model.

## Project Structure

```text
project-root/
├── frontend/           # React + Vite + Tailwind client
├── backend/            # Flask API for predictions
├── model/              # Shared feature extraction, training script, artifacts
├── dataset/            # CSV dataset used for training
├── README.md
└── .gitignore
```

## Features

- Clean React frontend with modern Tailwind UI
- Flask REST API with CORS and startup-time model loading
- ML pipeline based on handcrafted URL features and logistic regression
- URL validation and consistent error responses
- Deployment-ready config for Vercel frontend and Render backend
- Confidence score support in the UI and API

## Tech Stack

- Frontend: React, Vite, Tailwind CSS
- Backend: Flask, flask-cors, python-dotenv, scikit-learn
- ML: pandas, scikit-learn, DictVectorizer

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python ..\model\train_model.py
python app.py
```

The API will run on `http://localhost:5000`.

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The app will run on `http://localhost:5173`.

## Environment Variables

### Frontend

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:5000
```

### Backend

Create `backend/.env`:

```env
SECRET_KEY=replace_with_a_secure_random_value
MODEL_PATH=../model/model.pkl
VECTORIZER_PATH=../model/vectorizer.pkl
```

## Model Training

The training script reads `dataset/dataset.csv`, engineers URL-based phishing features, trains a logistic regression classifier, evaluates it, and writes:

- `model/model.pkl`
- `model/vectorizer.pkl`

Run:

```bash
python model/train_model.py
```

## API Contract

### `POST /predict`

Request:

```json
{
  "url": "example.com/login"
}
```

Response:

```json
{
  "result": "phishing",
  "confidence": 0.91,
  "normalized_url": "https://example.com/login"
}
```

Error response:

```json
{
  "error": "A valid URL is required."
}
```

## Deployment

### Frontend on Vercel

1. Import the `frontend` directory as the Vercel project root.
2. Set `VITE_API_URL` to your deployed backend URL.
3. Build command: `npm run build`
4. Output directory: `dist`

### Backend on Render

1. Create a new Web Service with `backend` as the root directory.
2. Install command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Add environment variables from `backend/.env.example`

## Security Notes

- `.env` files are gitignored
- Secrets stay on the backend only
- Input URLs are normalized and validated before prediction
- The ML model is loaded once at startup to avoid repeated disk I/O

## Notes

- The repository includes a sample phishing dataset copied into `dataset/dataset.csv`.
- The backend gracefully handles missing scheme values by normalizing to `https://` during validation.
