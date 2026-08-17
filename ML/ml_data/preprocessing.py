"""
preprocessing.py
Data cleaning and loading utilities.

DEMO PROTOTYPE — All data is synthetic.
"""

import os
import logging
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ─── Expected columns ────────────────────────────────────────────────────────────
REQUIRED_COLUMNS = {"source_ip", "url", "attack_type"}
ALL_COLUMNS = [
    "timestamp", "source_ip", "destination_ip",
    "method", "host", "url", "user_agent",
    "status_code", "response_size", "attack_type",
]


def load_dataset(path: Optional[str] = None) -> pd.DataFrame:
    """
    Load the synthetic CSV dataset.

    Parameters
    ----------
    path : str, optional
        Path to the CSV. Defaults to data/synthetic_traffic.csv
        relative to this file.

    Returns
    -------
    pd.DataFrame
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "data", "synthetic_traffic.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            "Run generate_dataset.py first."
        )

    df = pd.read_csv(path, dtype=str)
    logger.info(f"[load_dataset] Loaded {len(df)} rows from {path}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize a raw HTTP-record DataFrame.

    Steps
    -----
    1. Strip column names
    2. Drop rows missing required fields
    3. Normalize dtypes (status_code → int, response_size → int)
    4. Fill optional text fields with safe defaults
    5. Remove duplicate rows
    6. Reset index

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame (from load_dataset or an upload).

    Returns
    -------
    pd.DataFrame  — cleaned copy
    """
    df = df.copy()

    # 1. Strip column names
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. Drop rows without required fields
    before = len(df)
    df = df.dropna(subset=["source_ip", "url"])
    # If attack_type column exists, keep NaN as "Unknown" (inference path)
    if "attack_type" in df.columns:
        df["attack_type"] = df["attack_type"].fillna("Unknown")
    after = len(df)
    if before != after:
        logger.debug(f"[clean_data] Dropped {before - after} rows with missing source_ip/url")

    # 3. Normalize numeric fields
    df["status_code"] = pd.to_numeric(df.get("status_code", pd.Series(dtype=str)), errors="coerce").fillna(0).astype(int)
    df["response_size"] = pd.to_numeric(df.get("response_size", pd.Series(dtype=str)), errors="coerce").fillna(0).astype(int)

    # 4. Fill text fields
    text_defaults = {
        "method": "GET",
        "host": "",
        "user_agent": "",
        "destination_ip": "",
        "timestamp": "",
    }
    for col, default in text_defaults.items():
        if col in df.columns:
            df[col] = df[col].fillna(default).astype(str).str.strip()
        else:
            df[col] = default

    # 5. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    if before != after:
        logger.debug(f"[clean_data] Removed {before - after} duplicate rows")

    # 6. Reset index
    df = df.reset_index(drop=True)
    logger.info(f"[clean_data] Clean complete — {len(df)} rows remain")
    return df
