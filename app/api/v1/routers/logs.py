from fastapi import APIRouter, Query
from datetime import datetime
from typing import List, Dict, Optional
import boto3
import os
import re

router = APIRouter(prefix="/logs", tags=["Logs"])

# -------------------------------------------------
# Configuration
# -------------------------------------------------

LOG_GROUP = os.getenv("NETPILOT_LOG_GROUP", "/netpilot-ai/backend")
LOG_STREAM = os.getenv("NETPILOT_LOG_STREAM", "netpilot-backend")

logs_client = boto3.client("logs")

_LEVEL_RE = re.compile(r"\b(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\b")


def _infer_level(message: str) -> str:
    if not message:
        return "INFO"
    m = _LEVEL_RE.search(message)
    if not m:
        return "INFO"
    lvl = m.group(1)
    return "WARN" if lvl == "WARNING" else lvl


# -------------------------------------------------
# GET /api/v1/logs/recent
# -------------------------------------------------

@router.get("/recent")
def get_recent_logs(
    limit: int = Query(50, ge=1, le=200),
    next_token: Optional[str] = Query(default=None),
) -> Dict:
    """
    Return real backend application logs from AWS CloudWatch Logs.

    - Direct stream read (stable)
    - Read-only
    - Tail-style behavior (like aws logs tail)
    - Normalized for UI consumption
    """

    params = {
        "logGroupName": LOG_GROUP,
        "logStreamName": LOG_STREAM,
        "limit": limit,
        "startFromHead": False,
    }

    if next_token:
        params["nextToken"] = next_token

    try:
        response = logs_client.get_log_events(**params)

        events: List[Dict] = []
        for e in response.get("events", []):
            msg = (e.get("message") or "").strip()
            events.append(
                {
                    "timestamp": datetime.utcfromtimestamp(
                        e["timestamp"] / 1000
                    ).isoformat() + "Z",
                    "level": _infer_level(msg),
                    "message": msg,
                }
            )

        return {
            "status": "ok",
            "source": "cloudwatch",
            "log_group": LOG_GROUP,
            "log_stream": LOG_STREAM,
            "count": len(events),
            "next_token": response.get("nextForwardToken"),
            "logs": events,
        }

    except Exception as exc:
        return {
            "status": "error",
            "source": "cloudwatch",
            "log_group": LOG_GROUP,
            "log_stream": LOG_STREAM,
            "error": str(exc),
            "logs": [],
        }
