"""
model.py
Random Forest model: training, evaluation, save/load.

DEMO PROTOTYPE -- scikit-learn RandomForestClassifier only.
No deep learning. No artificial metric inflation.

All metrics are computed from actual test-set predictions.
"""

import os
import pickle
import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

# --- Model definition ------------------------------------------------------------

def build_model() -> RandomForestClassifier:
    """
    Return a configured (untrained) Random Forest classifier.
    Hyperparameters chosen for demo-scale data (~1,100 records).
    """
    return RandomForestClassifier(
        n_estimators=150,       # 150 trees -- good balance for ~1K records
        max_depth=None,         # Grow full trees
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",    # Standard RF recommendation
        class_weight="balanced",  # Handle class imbalance
        random_state=42,
        n_jobs=-1,
    )


# --- Training --------------------------------------------------------------------

def train_model(
    X: pd.DataFrame,
    y: pd.Series,
) -> Tuple[RandomForestClassifier, LabelEncoder]:
    """
    Fit a RandomForestClassifier on the provided feature matrix and labels.

    Parameters
    ----------
    X : pd.DataFrame  -- feature matrix (output of features.extract_features)
    y : pd.Series     -- string labels (attack_type column)

    Returns
    -------
    (trained_model, label_encoder)
    """
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    model = build_model()
    model.fit(X.values, y_encoded)

    logger.info(
        f"[train_model] Trained RF on {len(X)} samples, "
        f"{len(le.classes_)} classes: {list(le.classes_)}"
    )
    return model, le


# --- Evaluation ------------------------------------------------------------------

def evaluate_model(
    model: RandomForestClassifier,
    le: LabelEncoder,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """
    Evaluate the trained model on the held-out test set.
    Returns actual measured metrics -- no invented numbers.

    Parameters
    ----------
    model   : trained RandomForestClassifier
    le      : fitted LabelEncoder (same one used during training)
    X_test  : pd.DataFrame -- test feature matrix
    y_test  : pd.Series    -- true string labels

    Returns
    -------
    dict with keys:
        accuracy, precision, recall, f1,
        confusion_matrix, classification_report,
        classes
    """
    y_true_enc = le.transform(y_test)
    y_pred_enc = model.predict(X_test.values)

    accuracy  = round(accuracy_score(y_true_enc, y_pred_enc), 4)
    precision = round(precision_score(y_true_enc, y_pred_enc, average="weighted", zero_division=0), 4)
    recall    = round(recall_score(y_true_enc, y_pred_enc, average="weighted", zero_division=0), 4)
    f1        = round(f1_score(y_true_enc, y_pred_enc, average="weighted", zero_division=0), 4)

    cm = confusion_matrix(y_true_enc, y_pred_enc).tolist()
    report = classification_report(
        y_true_enc, y_pred_enc,
        target_names=le.classes_,
        zero_division=0,
    )

    metrics = {
        "accuracy":               accuracy,
        "precision":              precision,
        "recall":                 recall,
        "f1":                     f1,
        "confusion_matrix":       cm,
        "classification_report":  report,
        "classes":                list(le.classes_),
        "n_test_samples":         len(y_test),
        "note":                   "Prototype metrics -- synthetic data only",
    }

    logger.info(
        f"[evaluate_model] accuracy={accuracy:.4f}  "
        f"precision={precision:.4f}  recall={recall:.4f}  f1={f1:.4f}"
    )
    return metrics


# --- Persistence -----------------------------------------------------------------

def save_model(
    model: RandomForestClassifier,
    le: LabelEncoder,
    model_path: str = MODEL_PATH,
    encoder_path: str = ENCODER_PATH,
) -> None:
    """Persist model + label encoder to disk."""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(encoder_path, "wb") as f:
        pickle.dump(le, f)
    logger.info(f"[save_model] Model -> {model_path}")
    logger.info(f"[save_model] LabelEncoder -> {encoder_path}")


def load_model(
    model_path: str = MODEL_PATH,
    encoder_path: str = ENCODER_PATH,
) -> Tuple[RandomForestClassifier, LabelEncoder]:
    """
    Load a previously saved model + label encoder from disk.

    Raises
    ------
    FileNotFoundError if the model has not been trained yet.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No trained model found at {model_path}. "
            "Run train.py first: python ml_data/train.py"
        )
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(encoder_path, "rb") as f:
        le = pickle.load(f)
    logger.info(f"[load_model] Loaded model from {model_path}")
    return model, le


# --- Full pipeline helper ---------------------------------------------------------

def prepare_train_test(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
):
    """
    Stratified train/test split.

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
