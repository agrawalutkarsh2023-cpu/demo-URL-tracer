"""
models.py — SQLAlchemy ORM models for the demo database.
Tables: requests, detections, ip_analysis, uploads
All data is SYNTHETIC / DEMO only.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)          # "csv" | "pcap"
    records_processed = Column(Integer, default=0)
    attacks_detected = Column(Integer, default=0)
    high_risk_ips = Column(Integer, default=0)
    status = Column(String(20), default="pending")          # pending | completed | error
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)

    requests = relationship("Request", back_populates="upload")


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=True)
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=True)
    method = Column(String(10), nullable=True)
    host = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    response_size = Column(Integer, nullable=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)

    upload = relationship("Upload", back_populates="requests")
    detections = relationship("Detection", back_populates="request")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, index=True)
    attack_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False)           # LOW | MEDIUM | HIGH | CRITICAL
    confidence = Column(Float, nullable=False)
    detection_method = Column(String(20), nullable=False)   # RULE | ML | HYBRID
    result = Column(String(30), nullable=False)             # ATTEMPT | POTENTIAL_SUCCESS
    created_at = Column(DateTime, default=datetime.utcnow)

    # Snapshot of the originating request for easy querying
    source_ip = Column(String(45), nullable=True)
    url = Column(Text, nullable=True)
    host = Column(String(255), nullable=True)

    request = relationship("Request", back_populates="detections")


class IPAnalysis(Base):
    __tablename__ = "ip_analysis"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, unique=True, index=True)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW")          # LOW | MEDIUM | HIGH | CRITICAL
    attack_count = Column(Integer, default=0)
    request_count = Column(Integer, default=0)
    attack_types = Column(Text, nullable=True)              # JSON-encoded list
    last_seen = Column(DateTime, nullable=True)
    # Simulated geo — never real IPDR data
    geo_country = Column(String(100), default="Simulated")
    geo_city = Column(String(100), default="Simulated")
    isp = Column(String(200), default="Simulated ISP")
    first_seen = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
