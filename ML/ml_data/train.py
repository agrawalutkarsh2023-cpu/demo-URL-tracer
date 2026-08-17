"""
train.py
End-to-end training script.

Run:
    python ml_data/train.py

Pipeline:
    Generate (if needed) → Load → Clean → Extract Features →
    Train/Test Split → Train RF → Evaluate → Save

DEMO PROTOTYPE — synthetic data only.
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Make sure sibling modules are importable when run directly
sys.path.insert(0, os.path.dirname(__file__))

from generate_dataset import generate_dataset, OUTPUT_FILE
from preprocessing import load_dataset, clean_data
from features import extract_features, FEATURE_NAMES
from model import (
    train_model,
    evaluate_model,
    save_model,
    prepare_train_test,
)


def run_training_pipeline(force_regenerate: bool = False) -> dict:
    """
    Full training pipeline.

    Parameters
    ----------
    force_regenerate : bool
        If True, regenerate the synthetic dataset even if it already exists.

    Returns
    -------
    dict — evaluation metrics from the held-out test set
    """
    print("\n" + "=" * 60)
    print("  URL-Based Attack Detection — ML Training Pipeline")
    print("  DEMO PROTOTYPE  |  Synthetic data only")
    print("=" * 60)

    # ── Step 1: Dataset ──────────────────────────────────────────────────────────
    if force_regenerate or not os.path.exists(OUTPUT_FILE):
        print("\n[1/5] Generating synthetic dataset...")
        generate_dataset()
    else:
        print(f"\n[1/5] Dataset already exists → {OUTPUT_FILE}")

    # ── Step 2: Load & Clean ──────────────────────────────────────────────────────
    print("\n[2/5] Loading and cleaning data...")
    df_raw = load_dataset(OUTPUT_FILE)
    df = clean_data(df_raw)
    print(f"      Rows after cleaning: {len(df)}")

    label_counts = df["attack_type"].value_counts()
    print("\n      Label distribution:")
    for label, count in label_counts.items():
        bar = "█" * (count // 5)
        print(f"        {label:<30} {count:>4}  {bar}")

    # ── Step 3: Feature Extraction ───────────────────────────────────────────────
    print(f"\n[3/5] Extracting {len(FEATURE_NAMES)} features...")
    X = extract_features(df)
    y = df["attack_type"]
    print(f"      Feature matrix shape: {X.shape}")
    print(f"      Features: {', '.join(FEATURE_NAMES)}")

    # ── Step 4: Train / Test Split ───────────────────────────────────────────────
    print("\n[4/5] Splitting → 80% train / 20% test (stratified)...")
    X_train, X_test, y_train, y_test = prepare_train_test(X, y)
    print(f"      Train: {len(X_train)} samples  |  Test: {len(X_test)} samples")

    # ── Step 5: Train ────────────────────────────────────────────────────────────
    print("\n[5/5] Training Random Forest (n_estimators=150)...")
    model, le = train_model(X_train, y_train)
    print(f"      Classes: {list(le.classes_)}")

    # ── Evaluation ───────────────────────────────────────────────────────────────
    print("\n── Evaluation (test set) ──────────────────────────────")
    metrics = evaluate_model(model, le, X_test, y_test)

    print(f"  Accuracy  : {metrics['accuracy']:.4f}  ({metrics['accuracy']*100:.1f}%)")
    print(f"  Precision : {metrics['precision']:.4f}")
    print(f"  Recall    : {metrics['recall']:.4f}")
    print(f"  F1 Score  : {metrics['f1']:.4f}")
    print(f"\n  Per-class report:\n")
    print(metrics["classification_report"])

    # ── Save ─────────────────────────────────────────────────────────────────────
    save_model(model, le)
    print("\n✓ Model saved to ml_data/models/rf_model.pkl")
    print("✓ LabelEncoder saved to ml_data/models/label_encoder.pkl")

    # ── Feature importances ──────────────────────────────────────────────────────
    importances = model.feature_importances_
    print("\n── Feature Importances ───────────────────────────────")
    for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: -x[1]):
        bar = "█" * int(imp * 60)
        print(f"  {name:<30} {imp:.4f}  {bar}")

    print("\n" + "=" * 60)
    print("  Training complete.  Run predict.py to test predictions.")
    print("=" * 60 + "\n")

    return metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train the RF attack detection model.")
    parser.add_argument(
        "--regenerate", action="store_true",
        help="Force regeneration of the synthetic dataset before training."
    )
    args = parser.parse_args()
    run_training_pipeline(force_regenerate=args.regenerate)
