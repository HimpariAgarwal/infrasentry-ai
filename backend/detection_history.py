import os
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, String, Integer, Float,
    DateTime, JSON, desc
)
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing in backend/.env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class DetectionHistory(Base):
    __tablename__ = "detection_history"

    id = Column(String(36), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    model = Column(String(50), nullable=False)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    confidence_threshold = Column(Float, nullable=False)
    detections_count = Column(Integer, nullable=False)
    inference_time_ms = Column(Float, nullable=False)
    detections = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )


def initialize_history_database():
    Base.metadata.create_all(bind=engine)


def serialize_record(record):
    return {
        "id": record.id,
        "filename": record.filename,
        "model": record.model,
        "image_width": record.image_width,
        "image_height": record.image_height,
        "confidence_threshold": record.confidence_threshold,
        "detections_count": record.detections_count,
        "inference_time_ms": record.inference_time_ms,
        "detections": record.detections,
        "created_at": (
            record.created_at.isoformat()
            if record.created_at else None
        )
    }


def save_detection_record(result):
    db = SessionLocal()

    try:
        record = DetectionHistory(
            id=str(uuid4()),
            filename=result["filename"],
            model=result["model"],
            image_width=result["image_width"],
            image_height=result["image_height"],
            confidence_threshold=result["confidence_threshold"],
            detections_count=result["detections_count"],
            inference_time_ms=result["inference_time_ms"],
            detections=result["detections"]
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return serialize_record(record)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_detection_records(limit=50, offset=0):
    db = SessionLocal()

    try:
        total = db.query(DetectionHistory).count()

        records = (
            db.query(DetectionHistory)
            .order_by(desc(DetectionHistory.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "records": [serialize_record(item) for item in records]
        }
    finally:
        db.close()


def get_detection_record(record_id):
    db = SessionLocal()

    try:
        record = db.query(DetectionHistory).filter(
            DetectionHistory.id == record_id
        ).first()

        return serialize_record(record) if record else None
    finally:
        db.close()


def delete_detection_record(record_id):
    db = SessionLocal()

    try:
        record = db.query(DetectionHistory).filter(
            DetectionHistory.id == record_id
        ).first()

        if not record:
            return False

        db.delete(record)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
