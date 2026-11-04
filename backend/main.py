
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Create FastAPI application
app = FastAPI(
    title="InfraSentry AI",
    description="AI-powered Infrastructure Intelligence API",
    version="0.3.0"
)


# Allow React frontend to communicate with FastAPI
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


# Temporary in-memory report storage
reports = []


# Report data validation
class DamageReportCreate(BaseModel):
    damage_type: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=10, max_length=500)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    severity: int = Field(ge=1, le=5)


# Home endpoint
@app.get("/")
def home():
    return {
        "project": "InfraSentry AI",
        "status": "running",
        "message": "Welcome to InfraSentry AI"
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Backend is working correctly"
    }


# Create a new damage report
@app.post("/reports", status_code=201)
def create_report(report: DamageReportCreate):

    new_report = {
        "id": str(uuid4()),
        **report.model_dump(),
        "status": "submitted",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    reports.append(new_report)

    return {
        "message": "Damage report created successfully",
        "report": new_report
    }


# Get all damage reports
@app.get("/reports")
def get_reports():

    return {
        "count": len(reports),
        "reports": reports
    }


# Get a particular report using its ID
@app.get("/reports/{report_id}")
def get_report(report_id: str):

    for report in reports:
        if report["id"] == report_id:
            return report

    raise HTTPException(
        status_code=404,
        detail="Report not found"
    )
