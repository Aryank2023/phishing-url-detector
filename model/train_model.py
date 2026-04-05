from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from feature_extractor import extract_url_features

ROOT_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT_DIR / "dataset" / "dataset.csv"
MODEL_PATH = ROOT_DIR / "model" / "model.pkl"
VECTORIZER_PATH = ROOT_DIR / "model" / "vectorizer.pkl"


def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    dataset = pd.read_csv(csv_path)
    expected_columns = {"url", "label"}
    if not expected_columns.issubset(dataset.columns):
        raise ValueError(f"Dataset must contain columns: {sorted(expected_columns)}")

    dataset = dataset.dropna(subset=["url", "label"]).copy()
    dataset["url"] = dataset["url"].astype(str).str.strip()
    dataset["label"] = dataset["label"].astype(int)
    return dataset[dataset["url"] != ""]


def train() -> None:
    dataset = load_dataset(DATASET_PATH)
    feature_dicts = dataset["url"].map(extract_url_features).tolist()
    labels = dataset["label"].tolist()

    vectorizer = DictVectorizer(sparse=True)
    features = vectorizer.fit_transform(feature_dicts)

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        stratify=labels,
        random_state=42,
    )

    model = LogisticRegression(max_iter=3000, class_weight="balanced")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, target_names=["safe", "phishing"])

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print("Training complete.")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved vectorizer to: {VECTORIZER_PATH}")
    print(report)


if __name__ == "__main__":
    train()
