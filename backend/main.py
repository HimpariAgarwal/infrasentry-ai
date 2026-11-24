from backend.sla_scheduler_analytics_router import router as sla_scheduler_analytics_router
from backend.sla_scheduler import start_sla_scheduler, stop_sla_scheduler
from backend.sla_scheduler_router import router as sla_scheduler_router
from backend.sla_alerts_router import router as sla_alerts_router
from backend.sla_router import router as sla_router
from backend.incident_analytics_router import router as incident_analytics_router
from backend.incident_router import router as incident_router
from backend.alerts_router import router as alerts_router
from backend.threat_router import router as threat_router
from backend.security_router import router as security_router
from backend.api_access_control import APIAccessControlMiddleware
from auth_router import auth_router
from security_headers import SecurityHeadersMiddleware
from rate_limit import RateLimitMiddleware
from logs_router import router as logs_router
from api_logging import APILoggingMiddleware

import os
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from image_upload import router as image_upload_router


# --------------------------------------------------
# 1. ENVIRONMENT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Please check your backend/.env file."
    )


# --------------------------------------------------
# 2. DATABASE CONNECTION
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# --------------------------------------------------
# 3. DATABASE MODEL
# --------------------------------------------------

class DamageReport(Base):
    __tablename__ = "damage_reports"

    id = Column(String(36), primary_key=True, index=True)

    damage_type = Column(String(50), nullable=False)

    description = Column(String(500), nullable=False)

    latitude = Column(Float, nullable=False)

    longitude = Column(Float, nullable=False)

    severity = Column(Integer, nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="submitted"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


# Create tables if they do not already exist
Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# 4. PYDANTIC SCHEMAS
# --------------------------------------------------

class DamageReportCreate(BaseModel):

    damage_type: str = Field(
        min_length=3,
        max_length=50
    )

    description: str = Field(
        min_length=10,
        max_length=500
    )

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    severity: int = Field(
        ge=1,
        le=5
    )


class DamageReportUpdate(BaseModel):

    status: str = Field(
        pattern="^(submitted|under_review|resolved)$"
    )


# --------------------------------------------------
# 5. FASTAPI APPLICATION
# --------------------------------------------------

from system_router import router as system_router
from sla_scheduler_retry_metrics_router import router as sla_retry_metrics_router
from sla_scheduler_retry_profiles_router import router as sla_retry_profiles_router
from sla_scheduler_retry_preview_router import router as sla_retry_preview_router
from sla_scheduler_retry_comparison_router import router as sla_retry_comparison_router
app = FastAPI(
    title="InfraSentry AI API",
    description="AI-powered Road Infrastructure Intelligence Platform",
    version="1.0.0"
)
app.include_router(sla_retry_comparison_router)
app.include_router(sla_retry_preview_router)
app.include_router(sla_retry_profiles_router)
app.include_router(sla_retry_metrics_router)
app.include_router(sla_scheduler_analytics_router)
app.include_router(sla_scheduler_router)
app.include_router(sla_alerts_router)
app.include_router(sla_router)
app.include_router(incident_analytics_router)
app.include_router(incident_router)
app.include_router(alerts_router)
app.include_router(threat_router)
app.include_router(security_router)
app.add_middleware(APIAccessControlMiddleware)

app.include_router(auth_router)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=120,
    window_seconds=60,
)
app.include_router(logs_router)
app.add_middleware(APILoggingMiddleware)
app.include_router(system_router)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# 6. IMAGE UPLOAD ROUTER AND STATIC FILES
# --------------------------------------------------

app.include_router(image_upload_router)

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads"
)


# --------------------------------------------------
# 7. HELPER FUNCTION
# --------------------------------------------------

def report_to_dict(report):

    return {
        "id": report.id,
        "damage_type": report.damage_type,
        "description": report.description,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "severity": report.severity,
        "status": report.status,
        "created_at": report.created_at.isoformat()
        if report.created_at else None
    }


# --------------------------------------------------
# 8. ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to InfraSentry AI API",
        "status": "running",
        "version": "1.0.0"
    }


# --------------------------------------------------
# 9. HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "project": "InfraSentry AI"
    }


# --------------------------------------------------
# 10. DATABASE HEALTH CHECK
# --------------------------------------------------

@app.get("/db-health")
def database_health():

    db = SessionLocal()

    try:
        db.execute(func.now().select())

        return {
            "database": "connected",
            "status": "healthy"
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(error)}"
        )

    finally:
        db.close()


# --------------------------------------------------
# 11. CREATE ROAD DAMAGE REPORT
# --------------------------------------------------

@app.post("/reports")
def create_report(report: DamageReportCreate):

    db = SessionLocal()

    try:

        new_report = DamageReport(
            id=str(uuid4()),
            damage_type=report.damage_type,
            description=report.description,
            latitude=report.latitude,
            longitude=report.longitude,
            severity=report.severity,
            status="submitted"
        )

        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return {
            "message": "Road damage report created successfully",
            "report": report_to_dict(new_report)
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not create report: {str(error)}"
        )

    finally:
        db.close()


# --------------------------------------------------
# 12. GET ALL REPORTS
# --------------------------------------------------

@app.get("/reports")
def get_reports():

    db = SessionLocal()

    try:

        reports = (
            db.query(DamageReport)
            .order_by(DamageReport.created_at.desc())
            .all()
        )

        return [
            report_to_dict(report)
            for report in reports
        ]

    finally:
        db.close()


# --------------------------------------------------
# 13. GET SINGLE REPORT
# --------------------------------------------------

@app.get("/reports/{report_id}")
def get_report(report_id: str):

    db = SessionLocal()

    try:

        report = db.query(DamageReport).filter(
            DamageReport.id == report_id
        ).first()

        if not report:

            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        return report_to_dict(report)

    finally:
        db.close()


# --------------------------------------------------
# 14. UPDATE REPORT STATUS
# --------------------------------------------------

@app.put("/reports/{report_id}")
def update_report(
    report_id: str,
    update_data: DamageReportUpdate
):

    db = SessionLocal()

    try:

        report = db.query(DamageReport).filter(
            DamageReport.id == report_id
        ).first()

        if not report:

            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        report.status = update_data.status

        db.commit()
        db.refresh(report)

        return {
            "message": "Report status updated successfully",
            "report": report_to_dict(report)
        }

    finally:
        db.close()


# --------------------------------------------------
# 15. DELETE REPORT
# --------------------------------------------------

@app.delete("/reports/{report_id}")
def delete_report(report_id: str):

    db = SessionLocal()

    try:

        report = db.query(DamageReport).filter(
            DamageReport.id == report_id
        ).first()

        if not report:

            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        db.delete(report)
        db.commit()

        return {
            "message": "Report deleted successfully",
            "report_id": report_id
        }

    finally:
        db.close()


# --------------------------------------------------
# 16. GET REPORTS BY SEVERITY
# --------------------------------------------------

@app.get("/reports/severity/{severity}")
def get_reports_by_severity(severity: int):

    if severity < 1 or severity > 5:

        raise HTTPException(
            status_code=400,
            detail="Severity must be between 1 and 5"
        )

    db = SessionLocal()

    try:

        reports = db.query(DamageReport).filter(
            DamageReport.severity == severity
        ).all()

        return [
            report_to_dict(report)
            for report in reports
        ]

    finally:
        db.close()


# --------------------------------------------------
# 17. ANALYTICS SUMMARY
# --------------------------------------------------

@app.get("/analytics/summary")
def analytics_summary():

    db = SessionLocal()

    try:

        total_reports = db.query(
            DamageReport
        ).count()

        submitted = db.query(
            DamageReport
        ).filter(
            DamageReport.status == "submitted"
        ).count()

        under_review = db.query(
            DamageReport
        ).filter(
            DamageReport.status == "under_review"
        ).count()

        resolved = db.query(
            DamageReport
        ).filter(
            DamageReport.status == "resolved"
        ).count()

        severity_summary = {}

        for severity in range(1, 6):

            count = db.query(
                DamageReport
            ).filter(
                DamageReport.severity == severity
            ).count()

            severity_summary[str(severity)] = count

        average_severity = db.query(
            func.avg(DamageReport.severity)
        ).scalar()

        recent_reports = (
            db.query(DamageReport)
            .order_by(DamageReport.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "project": "InfraSentry AI",

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "total_reports": total_reports,

            "status_summary": {
                "submitted": submitted,
                "under_review": under_review,
                "resolved": resolved
            },

            "severity_summary": severity_summary,

            "average_severity": round(
                float(average_severity), 2
            ) if average_severity is not None else 0,

            "recent_reports": [
                report_to_dict(report)
                for report in recent_reports
            ]
        }

    finally:
        db.close()

# InfraSentry AI - YOLO detection API
try:
    from backend.ai_router import router as ai_router
except ModuleNotFoundError:
    from ai_router import router as ai_router

app.include_router(ai_router)
@app.on_event("startup")
def start_infrasentry_sla_scheduler():
    start_sla_scheduler()


@app.on_event("shutdown")
def stop_infrasentry_sla_scheduler():
    stop_sla_scheduler()
