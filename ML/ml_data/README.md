# ML System — URL-Based Cyber Attack Detection

> **DEMO PROTOTYPE** — All data is entirely synthetic. No real IPs, credentials, or victim data.

---

## Quick Start

```bash
# 1. Install ML dependencies (from /backend/)
pip install scikit-learn>=1.4.0 numpy>=1.26.0 pandas>=2.0.0

# 2. Train the model (from /ML/ml_data/)
python train.py

# 3. Test predictions
python predict.py
```

---

## File Structure

```
ml_data/
├── data/
│   └── synthetic_traffic.csv     # ~1,110 synthetic HTTP records (auto-generated)
├── models/
│   ├── rf_model.pkl              # Trained Random Forest (auto-generated)
│   ├── label_encoder.pkl         # Label encoder (auto-generated)
│   └── metrics.json              # Evaluation metrics (auto-generated)
├── generate_dataset.py           # Synthetic dataset generator
├── preprocessing.py              # load_dataset(), clean_data()
├── features.py                   # extract_features(), FEATURE_NAMES
├── model.py                      # train_model(), evaluate_model(), save/load
├── behavior.py                   # analyze_behavior(), get_ip_features()
├── train.py                      # End-to-end training script
├── predict.py                    # predict(), batch_predict(), get_model_status()
└── README.md
```

---

## Dataset

| Attack Class | Count |
|---|---|
| Normal | 200 |
| SQL Injection | 100 |
| XSS | 100 |
| Brute Force | 80 |
| Credential Stuffing | 80 |
| Directory Traversal | 80 |
| Command Injection | 80 |
| LFI/RFI | 70 |
| SSRF | 70 |
| HTTP Parameter Pollution | 70 |
| XXE | 60 |
| Web Shell Upload | 60 |
| Typosquatting | 60 |
| **Total** | **~1,110** |

Fields: `timestamp`, `source_ip`, `destination_ip`, `method`, `host`, `url`, `user_agent`, `status_code`, `response_size`, `attack_type`

---

## Feature List (13 features)

| Feature | Description |
|---|---|
| `url_length` | Total length of the URL string |
| `param_count` | Number of distinct query parameters |
| `special_char_count` | Count of `<>'"();|\\` etc. |
| `encoding_count` | Number of `%xx` percent-encoded sequences |
| `path_depth` | Number of path segments (e.g. `/a/b/c` → 3) |
| `suspicious_keyword_count` | Hits against SQL/XSS/CMD/traversal keyword list |
| `http_method_encoded` | GET=0, POST=1, PUT=2, DELETE=3… |
| `status_code` | HTTP response status code |
| `response_size` | Response body size in bytes |
| `has_dot_dot` | 1 if `../` or `%2e%2e` present |
| `has_base64` | 1 if long base64-like blob present in URL |
| `is_post` | 1 if method is POST |
| `query_length` | Length of the query string portion |

---

## Training Instructions

```bash
# From the ML/ml_data/ directory:

# Basic train (regenerates dataset if missing)
python train.py

# Force regenerate dataset + retrain
python train.py --regenerate
```

Output:
- Console: accuracy, precision, recall, F1, per-class report, feature importances
- `models/rf_model.pkl` — trained classifier
- `models/label_encoder.pkl` — string ↔ int label mapping
- `models/metrics.json` — metrics served by `/api/ml/metrics`

---

## Prediction Function

```python
from predict import predict, batch_predict, get_model_status

# Single prediction
result = predict({
    "url":           "/search?id=1' UNION SELECT * FROM users--",
    "method":        "GET",
    "host":          "demo-app.internal",
    "status_code":   200,
    "response_size": 1245,
})
# → {
#     "prediction":   "SQL Injection",
#     "confidence":   0.94,
#     "label":        "Prototype Prediction",
#     "model":        "RandomForest",
#     "ml_available": True
#   }

# If confidence < 0.55:
# → {"prediction": "LOW_CONFIDENCE", "confidence": 0.48, ...}

# Batch
results = batch_predict([rec1, rec2, rec3])

# Model info
status = get_model_status()
```

---

## Evaluation Metrics

Metrics are computed from the **actual held-out test set** (20% of data, stratified split).

Expected performance on synthetic data:
- Accuracy: ~88–95%
- F1 (weighted): ~88–94%

> ⚠️ These metrics reflect performance on **synthetic patterns only**. Real-world performance will differ significantly.

---

## Behavioral Analysis

```python
from behavior import analyze_behavior, get_ip_features

# Behavioral flags for one IP
alerts = analyze_behavior(df, "10.0.1.5")
# → [{"behavior": "Brute Force", "severity": "HIGH", "evidence": "..."}]

# Full IP feature profile
profile = get_ip_features(df, "10.0.1.5")
# → {
#     "ip_address": "10.0.1.5",
#     "total_requests": 87,
#     "attack_count": 42,
#     "attack_types": ["SQL Injection", "Brute Force"],
#     "request_frequency_per_min": 14.2,
#     "first_seen": "2024-06-01T00:00:12",
#     "last_seen":  "2024-06-01T01:05:33",
#     "behavioral_alerts": [...]
#   }
```

---

## Backend Integration

The backend uses `services/ml_service.py` as the single integration point:

```python
from services.ml_service import predict, batch_predict, get_ml_status

# Called automatically in csv_service.py and upload.py
result = predict(request_record)
```

**Graceful degradation**: If `rf_model.pkl` is not found (model not yet trained),
`ml_service.py` automatically falls back to the keyword-heuristic stub.
The backend continues to work without any changes.

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| `GET`  | `/api/ml/status` | Model availability, class list |
| `POST` | `/api/ml/predict` | Single-record RF prediction |
| `POST` | `/api/ml/predict/batch` | Batch predictions (max 500) |
| `GET`  | `/api/ml/metrics` | Evaluation metrics from training |

---

## Important Disclaimers

- All data is **100% synthetic** — generated by `generate_dataset.py`
- No real IPs, credentials, victims, or IPDR data
- All predictions carry the label: **"Prototype Prediction"**
- Do **not** claim "Production AI" or "100% accurate"
- ML is a **supporting component** — rule-based detection runs first
