"""
api/export.py
GET /api/export/csv  — Download all detections as a CSV file.
GET /api/export/json — Download all detections + IP analysis as JSON.
"""

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Detection, IPAnalysis, Request

router = APIRouter()


@router.get("/export/csv", tags=["Export"])
def export_csv(db: Session = Depends(get_db)):
    """
    Stream all detections as a downloadable CSV file.
    Columns: id, request_id, attack_type, severity, confidence,
             detection_method, result, source_ip, url, host, created_at
    """
    detections = db.query(Detection).order_by(Detection.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id", "request_id", "attack_type", "severity", "confidence",
        "detection_method", "result", "source_ip", "url", "host", "created_at",
    ])

    for d in detections:
        writer.writerow([
            d.id,
            d.request_id,
            d.attack_type,
            d.severity,
            d.confidence,
            d.detection_method,
            d.result,
            d.source_ip,
            d.url,
            d.host,
            d.created_at.isoformat() if d.created_at else "",
        ])

    output.seek(0)
    filename = f"attack_detections_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/json", tags=["Export"])
def export_json(db: Session = Depends(get_db)):
    """
    Return all detections and IP analysis as a JSON download.

    Structure:
    {
        "exported_at": "...",
        "note": "SYNTHETIC / DEMO DATA ONLY",
        "detections": [...],
        "ip_analysis": [...]
    }
    """
    detections = db.query(Detection).order_by(Detection.created_at.desc()).all()
    ip_list = db.query(IPAnalysis).order_by(IPAnalysis.risk_score.desc()).all()

    det_data = [
        {
            "id": d.id,
            "request_id": d.request_id,
            "attack_type": d.attack_type,
            "severity": d.severity,
            "confidence": d.confidence,
            "detection_method": d.detection_method,
            "result": d.result,
            "source_ip": d.source_ip,
            "url": d.url,
            "host": d.host,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in detections
    ]

    ip_data = [
        {
            "ip_address": ip.ip_address,
            "risk_score": ip.risk_score,
            "risk_level": ip.risk_level,
            "attack_count": ip.attack_count,
            "request_count": ip.request_count,
            "attack_types": json.loads(ip.attack_types or "[]"),
            "last_seen": ip.last_seen.isoformat() if ip.last_seen else None,
            "geo_country": ip.geo_country,
            "geo_city": ip.geo_city,
            "isp": ip.isp,
        }
        for ip in ip_list
    ]

    payload = {
        "exported_at": datetime.utcnow().isoformat(),
        "note": "SYNTHETIC / DEMO DATA ONLY — Not real cyberattack data",
        "total_detections": len(det_data),
        "total_ips_analysed": len(ip_data),
        "detections": det_data,
        "ip_analysis": ip_data,
    }

    filename = f"attack_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    json_bytes = json.dumps(payload, indent=2).encode("utf-8")

    return StreamingResponse(
        iter([json_bytes]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
