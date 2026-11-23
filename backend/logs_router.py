from pathlib import Path
import csv
import io

from fastapi import APIRouter, Query, Response

router = APIRouter(prefix="/api/v1/logs", tags=["API Logs"])

LOG_FILE = Path(__file__).resolve().parent / "logs" / "api.log"


def read_logs():
    if not LOG_FILE.exists():
        return []

    entries = []
    for line in LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(" | ", 2)
        if len(parts) == 3:
            entries.append({
                "timestamp": parts[0],
                "level": parts[1],
                "message": parts[2],
            })
    return entries


@router.get("")
def get_logs(
    search: str = Query(default="", max_length=200),
    level: str = Query(default="ALL", max_length=20),
    limit: int = Query(default=200, ge=1, le=1000),
):
    entries = read_logs()

    if level.upper() != "ALL":
        entries = [entry for entry in entries if entry["level"].upper() == level.upper()]

    if search:
        term = search.lower()
        entries = [
            entry for entry in entries
            if term in entry["message"].lower()
            or term in entry["timestamp"].lower()
        ]

    entries = list(reversed(entries[-limit:]))

    return {
        "total": len(entries),
        "logs": entries,
    }


@router.get("/export")
def export_logs():
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["timestamp", "level", "message"]
    )
    writer.writeheader()
    writer.writerows(read_logs())

    return Response(
        content="\ufeff" + output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=infrasentry-api-logs.csv"},
    )


@router.delete("")
def clear_logs():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text("", encoding="utf-8")
    return {"message": "API logs cleared successfully"}
