"""
api/ips.py
GET /api/ips        — List all analysed IPs with risk levels.
GET /api/ips/{ip}   — Full IP profile: risk score, attack history, geo (simulated).
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models import IPAnalysis, Detection
from schemas import IPListResponse, IPAnalysisOut

router = APIRouter()


@router.get("/ips", response_model=IPListResponse, tags=["IP Analysis"])
def list_ips(
    risk_level: Optional[str] = Query(None, description="Filter by risk level: LOW|MEDIUM|HIGH|CRITICAL"),
    min_score: Optional[int] = Query(None, description="Minimum risk score"),
    db: Session = Depends(get_db),
):
    """
    Returns all analysed IPs sorted by risk score descending.
    """
    q = db.query(IPAnalysis)

    if risk_level:
        q = q.filter(IPAnalysis.risk_level == risk_level.upper())
    if min_score is not None:
        q = q.filter(IPAnalysis.risk_score >= min_score)

    total = q.count()
    items = q.order_by(desc(IPAnalysis.risk_score)).all()

    return IPListResponse(
        total=total,
        items=[IPAnalysisOut.model_validate(ip) for ip in items],
    )


@router.get("/ips/{ip_address}", tags=["IP Analysis"])
def get_ip_profile(ip_address: str, db: Session = Depends(get_db)):
    """
    Returns a full profile for a single IP address including:
    - Risk score and level
    - All associated detections
    - Simulated geo / ISP data
    """
    # Validate format roughly
    ip_address = ip_address.strip()

    ip = db.query(IPAnalysis).filter(IPAnalysis.ip_address == ip_address).first()
    if not ip:
        raise HTTPException(status_code=404, detail=f"IP {ip_address} not found in analysis database.")

    # Fetch associated detections for this IP
    detections = (
        db.query(Detection)
        .filter(Detection.source_ip == ip_address)
        .order_by(Detection.created_at.desc())
        .limit(100)
        .all()
    )

    detection_list = [
        {
            "id": d.id,
            "attack_type": d.attack_type,
            "severity": d.severity,
            "confidence": d.confidence,
            "detection_method": d.detection_method,
            "result": d.result,
            "url": d.url,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in detections
    ]

    attack_types_list = json.loads(ip.attack_types or "[]")

    return {
        "ip_address": ip.ip_address,
        "risk_score": ip.risk_score,
        "risk_level": ip.risk_level,
        "attack_count": ip.attack_count,
        "request_count": ip.request_count,
        "attack_types": attack_types_list,
        "last_seen": ip.last_seen.isoformat() if ip.last_seen else None,
        "first_seen": ip.first_seen.isoformat() if ip.first_seen else None,
        "geo": {
            "country": ip.geo_country,
            "city": ip.geo_city,
            "isp": ip.isp,
            "note": "Simulated geo data — not real IPDR information",
        },
        "detections": detection_list,
    }
