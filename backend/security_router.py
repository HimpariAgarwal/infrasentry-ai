import json
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/security", tags=["Security"])

LOG_FILE = Path(__file__).resolve().parent / "logs" / "security_audit.log"


@router.get("/audit")
def get_security_audit(
    limit: int = Query(100, ge=1, le=500),
    event: str = Query("all"),
):
    if not LOG_FILE.exists():
        return {"total": 0, "events": []}

    records = []

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                item = json.loads(line)
                if event == "all" or item.get("event") == event:
                    records.append(item)
            except json.JSONDecodeError:
                continue

    records.reverse()
    return {
        "total": len(records),
        "events": records[:limit],
    }
