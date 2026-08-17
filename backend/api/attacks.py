"""
api/attacks.py
GET /api/attacks        — Paginated, filtered list of detections.
GET /api/attacks/{id}   — Single detection detail with linked request.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Detection, Request
from schemas import AttackListResponse, DetectionOut

router = APIRouter()


@router.get("/attacks", response_model=AttackListResponse, tags=["Attacks"])
def list_attacks(
    attack_type: Optional[str] = Query(None, description="Filter by attack type"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW|MEDIUM|HIGH|CRITICAL"),
    result: Optional[str] = Query(None, description="Filter by result: ATTEMPT|POTENTIAL_SUCCESS"),
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of all detections with optional filters.
    Ordered by created_at descending (most recent first).
    """
    q = db.query(Detection)

    if attack_type:
        q = q.filter(Detection.attack_type.ilike(f"%{attack_type}%"))
    if severity:
        q = q.filter(Detection.severity == severity.upper())
    if result:
        q = q.filter(Detection.result == result.upper())
    if source_ip:
        q = q.filter(Detection.source_ip == source_ip)

    total = q.count()
    items = (
        q.order_by(Detection.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AttackListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[DetectionOut.model_validate(d) for d in items],
    )


@router.get("/attacks/{attack_id}", response_model=DetectionOut, tags=["Attacks"])
def get_attack(attack_id: int, db: Session = Depends(get_db)):
    """
    Returns full detail for a single detection by ID.
    """
    det = db.query(Detection).filter(Detection.id == attack_id).first()
    if not det:
        raise HTTPException(status_code=404, detail=f"Detection {attack_id} not found.")
    return DetectionOut.model_validate(det)
