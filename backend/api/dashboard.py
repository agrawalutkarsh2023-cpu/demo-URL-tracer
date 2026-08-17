"""
api/dashboard.py
GET /api/dashboard — Aggregate statistics for the frontend dashboard.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends

from database import get_db
from models import Request, Detection, IPAnalysis
from schemas import (
    DashboardResponse, AttackTypeStat, SeverityStat, TopIP, DetectionOut
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
def get_dashboard(db: Session = Depends(get_db)):
    """
    Returns aggregate stats:
    - Total requests and attacks
    - Attacks grouped by type and severity
    - Top attacking IPs
    - Recent detections
    - Potential success count (simulated)
    """
    total_requests = db.query(func.count(Request.id)).scalar() or 0
    total_attacks = db.query(func.count(Detection.id)).scalar() or 0

    # IPs with risk level HIGH or CRITICAL
    high_risk_ips = (
        db.query(func.count(IPAnalysis.id))
        .filter(IPAnalysis.risk_level.in_(["HIGH", "CRITICAL"]))
        .scalar() or 0
    )
    critical_ips = (
        db.query(func.count(IPAnalysis.id))
        .filter(IPAnalysis.risk_level == "CRITICAL")
        .scalar() or 0
    )

    # Attacks by type
    type_rows = (
        db.query(Detection.attack_type, func.count(Detection.id).label("cnt"))
        .group_by(Detection.attack_type)
        .order_by(func.count(Detection.id).desc())
        .all()
    )
    attacks_by_type = [AttackTypeStat(attack_type=r[0], count=r[1]) for r in type_rows]

    # Attacks by severity
    sev_rows = (
        db.query(Detection.severity, func.count(Detection.id).label("cnt"))
        .group_by(Detection.severity)
        .order_by(func.count(Detection.id).desc())
        .all()
    )
    attacks_by_severity = [SeverityStat(severity=r[0], count=r[1]) for r in sev_rows]

    # Top 10 attacking IPs
    top_ips = (
        db.query(IPAnalysis)
        .filter(IPAnalysis.attack_count > 0)
        .order_by(IPAnalysis.risk_score.desc())
        .limit(10)
        .all()
    )
    top_attacking_ips = [
        TopIP(
            ip_address=ip.ip_address,
            risk_score=ip.risk_score,
            risk_level=ip.risk_level,
            attack_count=ip.attack_count,
        )
        for ip in top_ips
    ]

    # 20 most recent detections
    recent = (
        db.query(Detection)
        .order_by(Detection.created_at.desc())
        .limit(20)
        .all()
    )
    recent_detections = [DetectionOut.model_validate(d) for d in recent]

    # Simulated success count
    potential_success_count = (
        db.query(func.count(Detection.id))
        .filter(Detection.result == "POTENTIAL_SUCCESS")
        .scalar() or 0
    )

    return DashboardResponse(
        total_requests=total_requests,
        total_attacks=total_attacks,
        high_risk_ips=high_risk_ips,
        critical_ips=critical_ips,
        attacks_by_type=attacks_by_type,
        attacks_by_severity=attacks_by_severity,
        top_attacking_ips=top_attacking_ips,
        recent_detections=recent_detections,
        potential_success_count=potential_success_count,
    )
