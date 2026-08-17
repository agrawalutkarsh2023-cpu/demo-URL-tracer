"""
main.py — FastAPI application entry point.

URL-Based Cyber Attack Detection & IP Intelligence System
DEMO PROTOTYPE — All data is SYNTHETIC. Not connected to live traffic.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, SessionLocal
from models import Base
from utils.seed import seed_database

from api import dashboard, attacks, ips, upload, export, ml


# ─────────────────────────────────────────────
# Startup / Shutdown lifecycle
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Seed demo data if database is empty
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    yield  # server is running

    # (Shutdown logic can go here if needed)


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────

app = FastAPI(
    title="URL-Based Cyber Attack Detection & IP Intelligence System",
    description=(
        "DEMO PROTOTYPE — Demonstrates detection of URL-based cyberattacks "
        "from synthetic HTTP/IP data. All data is simulated. "
        "Not connected to live traffic, real credentials, or real victims."
    ),
    version="1.0.0",
    contact={"name": "Hackathon Team", "email": "demo@example.com"},
    license_info={"name": "Demo Only"},
    lifespan=lifespan,
)

# ─────────────────────────────────────────────
# CORS — allow all origins for the hackathon demo
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Global exception handler — never expose stack traces
# ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred."},
    )


# ─────────────────────────────────────────────
# Register API routers
# ─────────────────────────────────────────────

app.include_router(dashboard.router, prefix="/api")
app.include_router(attacks.router, prefix="/api")
app.include_router(ips.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(ml.router, prefix="/api")


# ─────────────────────────────────────────────
# Root health check
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "system": "URL-Based Cyber Attack Detection & IP Intelligence System",
        "mode": "DEMO — Synthetic data only",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
