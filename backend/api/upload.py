"""
api/upload.py
POST /api/upload/csv  — Upload and process a synthetic CSV file.
POST /api/upload/pcap — Upload and process a PCAP file.

All uploaded data is SYNTHETIC / DEMO only.
"""

import os
import uuid
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import UploadResponse
from services.csv_service import process_csv_upload, CSVValidationError
from services.pcap_service import process_pcap
from services.csv_service import _upsert_ip_analysis   # reuse for PCAP pipeline
from detection.engine import run_detection
from services.ml_service import predict
from models import Request, Detection, Upload
from datetime import datetime
from utils.normalizer import parse_timestamp

router = APIRouter()

_ALLOWED_CSV_TYPES = {"text/csv", "application/csv", "application/vnd.ms-excel", "text/plain"}
_ALLOWED_PCAP_TYPES = {"application/octet-stream", "application/vnd.tcpdump.pcap"}
_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ─────────────────────────────────────────────
# CSV Upload
# ─────────────────────────────────────────────

@router.post("/upload/csv", response_model=UploadResponse, tags=["Upload"])
async def upload_csv(
    file: UploadFile = File(..., description="CSV file with HTTP request records"),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file containing synthetic HTTP request records.

    The backend will:
    1. Validate the CSV structure
    2. Normalize column names
    3. Run rule-based + ML detection on each record
    4. Calculate IP risk scores
    5. Store results in SQLite
    6. Return a processing summary
    """
    # Validate file extension
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a .csv file.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50 MB.")

    try:
        result = process_csv_upload(content, file.filename or "upload.csv", db)
    except CSVValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while processing the CSV. Please check the file format.")

    return UploadResponse(**result)


# ─────────────────────────────────────────────
# PCAP Upload
# ─────────────────────────────────────────────

@router.post("/upload/pcap", response_model=UploadResponse, tags=["Upload"])
async def upload_pcap(
    file: UploadFile = File(..., description="PCAP or PCAPNG network capture file"),
    db: Session = Depends(get_db),
):
    """
    Upload a PCAP file. The backend will:
    1. Extract simulated HTTP records via the PCAP module
    2. Run detection on each record
    3. Calculate IP risk scores
    4. Store results in SQLite
    5. Return a summary

    Note: In this demo, the PCAP module generates synthetic records
    seeded from the file size.
    """
    fname = (file.filename or "upload.pcap").lower()
    if not (fname.endswith(".pcap") or fname.endswith(".pcapng") or fname.endswith(".cap")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a .pcap or .pcapng file.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50 MB.")

    # Write to temp file so pcap_service can os.path operations
    suffix = ".pcapng" if fname.endswith(".pcapng") else ".pcap"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    # Create upload record
    upload = Upload(
        filename=file.filename or "upload.pcap",
        file_type="pcap",
        status="processing",
        uploaded_at=datetime.utcnow(),
    )
    db.add(upload)
    db.flush()

    try:
        records = process_pcap(tmp_path)
    except Exception as e:
        upload.status = "error"
        upload.error_message = str(e)[:500]
        db.commit()
        raise HTTPException(status_code=422, detail=f"PCAP processing failed: {str(e)}")
    finally:
        os.unlink(tmp_path)

    # Run the same detection pipeline as CSV
    ip_detections: dict[str, list[dict]] = {}
    ip_request_counts: dict[str, int] = {}
    records_processed = 0
    attacks_detected = 0

    for record in records:
        src_ip = record.get("source_ip", "0.0.0.0")
        ip_request_counts[src_ip] = ip_request_counts.get(src_ip, 0) + 1

        req_obj = Request(
            timestamp=parse_timestamp(record.get("timestamp")),
            source_ip=src_ip,
            destination_ip=record.get("destination_ip"),
            method=record.get("method"),
            host=record.get("host"),
            url=record.get("url"),
            user_agent=record.get("user_agent"),
            status_code=record.get("status_code"),
            response_size=record.get("response_size"),
            upload_id=upload.id,
        )
        db.add(req_obj)
        db.flush()

        det_result = run_detection(record)

        if det_result is None:
            ml_out = predict(record)
            if ml_out["prediction"] != "Benign" and ml_out["confidence"] >= 0.70:
                det_result = {
                    "attack_type": ml_out["prediction"],
                    "severity": "MEDIUM",
                    "confidence": ml_out["confidence"],
                    "detection_method": "ML",
                    "result": "ATTEMPT",
                }
        elif det_result:
            det_result["detection_method"] = "HYBRID"

        if det_result:
            det_obj = Detection(
                request_id=req_obj.id,
                attack_type=det_result["attack_type"],
                severity=det_result["severity"],
                confidence=det_result["confidence"],
                detection_method=det_result["detection_method"],
                result=det_result["result"],
                source_ip=src_ip,
                url=record.get("url"),
                host=record.get("host"),
            )
            db.add(det_obj)
            attacks_detected += 1
            ip_detections.setdefault(src_ip, []).append(det_result)

        records_processed += 1

    high_risk_ips = _upsert_ip_analysis(db, ip_detections, ip_request_counts)

    upload.records_processed = records_processed
    upload.attacks_detected = attacks_detected
    upload.high_risk_ips = high_risk_ips
    upload.status = "completed"
    db.commit()

    return UploadResponse(
        status="completed",
        upload_id=upload.id,
        records_processed=records_processed,
        attacks_detected=attacks_detected,
        high_risk_ips=high_risk_ips,
    )
