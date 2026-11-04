
from datetime import datetime, timezone
from uuid import uuid4
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# Load environment variables from backend/.env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Check your backend/.env file."
    )


# Connect to PostgreSQL
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


# Database table
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
        default="submitted",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


# Create table if it does not exist
Base.metadata.create_all(bind=engine)


# FastAPI application
app = FastAPI(
    title="InfraSentry AI",
    description="AI-powered Infrastructure Intelligence API",
    version="0.4.0"
)


# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database session dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Input validation
class DamageReportCreate(BaseModel):
    damage_type: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=10, max_length=500)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    severity: int = Field(ge=1, le=5)


# Convert database object into JSON-friendly dictionary
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
    }


# Home endpoint
@app.get("/")
def home():
    return {
        "project": "InfraSentry AI",
        "status": "running",
        "message": "Welcome to InfraSentry AI"
    }


# Backend health check
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Backend is working correctly"
    }


# Database health check
@app.get("/db-health")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "status": "healthy"
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(error)}"
        )


# Create a new damage report
@app.post("/reports", status_code=201)
def create_report(
    report: DamageReportCreate,
    db: Session = Depends(get_db)
):

    new_report = DamageReport(
        id=str(uuid4()),
        damage_type=report.damage_type,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        severity=report.severity,
        status="submitted",
        created_at=datetime.now(timezone.utc)
    )

    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return {
            "message": "Damage report created successfully",
            "report": report_to_dict(new_report)
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save damage report"
        )


# Get all damage reports
@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):

    all_reports = (
        db.query(DamageReport)
        .order_by(DamageReport.created_at.desc())
        .all()
    )

    return {
        "count": len(all_reports),
        "reports": [
            report_to_dict(report)
            for report in all_reports
        ]
    }


# Get one damage report by ID
@app.get("/reports/{report_id}")
def get_report(
    report_id: str,
    db: Session = Depends(get_db)
):

    report = (
        db.query(DamageReport)
        .filter(DamageReport.id == report_id)
        .first()
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report_to_dict(report)
