import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_FILE = LOG_DIR / "security_audit.log"

logger = logging.getLogger("infrasentry.security")
logger.setLevel(logging.WARNING)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(AUDIT_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def record_security_event(
    event: str,
    path: str,
    ip_address: str,
    reason: str,
):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "path": path,
        "ip_address": ip_address,
        "reason": reason,
    }

    logger.warning(json.dumps(entry))
