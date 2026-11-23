import os
from pathlib import Path
import platform
import time
from datetime import datetime, timezone

import psutil
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

START_TIME = time.time()

def get_database_status():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return {
            "connected": False,
            "status": "not_configured",
        }

    try:
        engine = create_engine(database_url, pool_pre_ping=True)

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        engine.dispose()

        return {
            "connected": True,
            "status": "connected",
        }

    except (SQLAlchemyError, Exception) as error:
        return {
            "connected": False,
            "status": "disconnected",
            "error": str(error)[:200],
        }


def get_system_health():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))

    cpu_percent = psutil.cpu_percent(interval=0.2)

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "system": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "cpu_percent": cpu_percent,
            "cpu_count": psutil.cpu_count(logical=True),
            "memory": {
                "total_mb": round(memory.total / (1024 ** 2), 2),
                "used_mb": round(memory.used / (1024 ** 2), 2),
                "available_mb": round(memory.available / (1024 ** 2), 2),
                "percent": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "used_gb": round(disk.used / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "percent": disk.percent,
            },
        },
        "database": get_database_status(),
    }
