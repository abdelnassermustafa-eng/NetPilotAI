from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from app.core.memory_log_handler import memory_logs
import boto3
import os

router = APIRouter(prefix="/logs", tags=["Logs"])

# -------------------------------------------------
# Local-dev fallback logs (safe, deterministic)
# -------------------------------------------------
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

    Priority order:
    1. In-memory live backend logs
    2. Local-dev fallback logs
    3. CloudWatch (AWS only)
    """

    # -------------------------------------------------
    # Phase 5.3 — ALWAYS return in-memory logs first
    # -------------------------------------------------
    if memory_logs:
        return {
            "status": "ok",
            "source": "memory",
            "count": min(len(memory_logs), limit),
            "logs": list(memory_logs)[-limit:],
        }

    # -------------------------------------------------
    # Local-dev fallback (no AWS)
    # -------------------------------------------------
    if os.getenv("AWS_EXECUTION_ENV") is None:
        return {
            "status": "ok",
            "source": "local-dev",
            "count": len(_LOCAL_DEV_LOGS),
            "logs": _LOCAL_DEV_LOGS[-limit:],
        }

    # -------------------------------------------------
    # CloudWatch (AWS only)
    # -------------------------------------------------
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
                "level": "INFO",
                "message": e.get("message", "").strip(),
            }
            for e in response.get("events", [])
        ]

        return {
            "status": "ok",
            "source": "cloudwatch",
            "count": len(events),
            "logs": events,
        }

    except Exception as exc:
        return {
            "status": "error",
            "source": "cloudwatch",
            "error": str(exc),
            "logs": [],
        }
