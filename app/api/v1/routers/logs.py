from fastapi import APIRouter, Query
from datetime import datetime, timedelta
import boto3
import os

router = APIRouter(prefix="/logs", tags=["Logs"])

# -----------------------------
# Local-dev fallback logs
# -----------------------------
_LOCAL_DEV_LOGS = [
    {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "message": "NetPilot backend started successfully",
    },
    {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "message": "Observability logs endpoint initialized",
    },
]

@router.get("/recent")
def get_recent_logs(
    window: int = Query(15, ge=1, le=120),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Return recent backend logs.
    CloudWatch in AWS, safe local fallback in dev.
    Read-only, bounded, UI-safe.
    """

    # ----------------------------------
    # If not running in AWS, fallback
    # ----------------------------------
    if os.getenv("AWS_EXECUTION_ENV") is None:
        return {
            "status": "ok",
            "source": "local-dev",
            "window_minutes": window,
            "count": len(_LOCAL_DEV_LOGS),
            "logs": _LOCAL_DEV_LOGS[:limit],
        }

    # ----------------------------------
    # CloudWatch Logs (AWS)
    # ----------------------------------
    logs_client = boto3.client("logs")
    start_time = int(
        (datetime.utcnow() - timedelta(minutes=window)).timestamp() * 1000
    )

    try:
        response = logs_client.filter_log_events(
            logGroupName="/netpilot-ai/backend",
            startTime=start_time,
            limit=limit,
        )

        events = [
            {
                "timestamp": datetime.utcfromtimestamp(
                    e["timestamp"] / 1000
                ).isoformat() + "Z",
                "level": "INFO",  # CloudWatch does not guarantee level parsing
                "message": e.get("message", "").strip(),
            }
            for e in response.get("events", [])
        ]

        return {
            "status": "ok",
            "source": "cloudwatch",
            "window_minutes": window,
            "count": len(events),
            "logs": events,
        }

    except Exception as exc:
        # Never break UI
        return {
            "status": "error",
            "source": "cloudwatch",
            "error": str(exc),
            "logs": [],
        }
