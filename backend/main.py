
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="InfraSentry AI",
    description="Infrastructure Damage Reporting API",
    version="0.2.0"
)

# Temporary in-memory storage
reports = []


# Data required to create a report
class DamageReportCreate(BaseModel):
    damage_type: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=10, max_length=500)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    severity: int = Field(ge=1, le=5)


# Home API
@app.get("/")
def home():
    return {
        "project": "InfraSentry AI",
        "status": "running",
        "message": "Infrastructure Intelligence API"
    }


# Health check API
@app.get("/health")
def health():
    return {"status": "healthy"}


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


# Get one report using its ID
@app.get("/reports/{report_id}")
def get_report(report_id: str):

    for report in reports:
        if report["id"] == report_id:
            return report

    raise HTTPException(
        status_code=404,
        detail="Report not found"
    )
