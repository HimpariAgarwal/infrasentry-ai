import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def collect_system_diagnostics(
    path=None,
    disk_warning_threshold=90.0,
):
    """
    Collect safe, non-sensitive system diagnostics.

    No credentials, environment variables, or secret values
    are collected or returned.
    """

    if not 0 <= disk_warning_threshold <= 100:
        raise ValueError("Disk warning threshold must be between 0 and 100.")

    target = Path(path) if path is not None else Path(__file__).resolve().parent

    disk = shutil.disk_usage(str(target))

    total_bytes = disk.total
    used_bytes = disk.used
    free_bytes = disk.free

    usage_percent = (
        round((used_bytes / total_bytes) * 100, 2)
        if total_bytes > 0
        else 0.0
    )

    disk_status = (
        "warning"
        if usage_percent >= disk_warning_threshold
        else "healthy"
    )

    checks = [
        {
            "name": "disk_space",
            "status": disk_status,
            "details": {
                "total_bytes": total_bytes,
                "used_bytes": used_bytes,
                "free_bytes": free_bytes,
                "usage_percent": usage_percent,
                "warning_threshold": disk_warning_threshold,
            },
        },
        {
            "name": "python_runtime",
            "status": "healthy",
            "details": {
                "python_version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.system(),
            },
        },
    ]

    failed_checks = sum(
        1 for check in checks
        if check["status"] != "healthy"
    )

    return {
        "service": "InfraSentry AI",
        "status": "degraded" if failed_checks else "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "checks": checks,
        "summary": {
            "total": len(checks),
            "healthy": len(checks) - failed_checks,
            "degraded": failed_checks,
        },
    }
