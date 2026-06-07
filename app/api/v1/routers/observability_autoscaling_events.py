from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Query

from app.services.observability.events.cloudwatch_logs_reader import fetch_log_events_json
from app.services.observability.events.autoscaling_normalizer import normalize_autoscaling_event

router = APIRouter(
    prefix="/api/v1/observability/autoscaling",
    tags=["Observability - Auto Scaling Events"],
)


LOG_GROUP_DEFAULT = "/aws/events/netpilot-autoscaling"


@router.get("/events")
def get_autoscaling_events(
    minutes: int = Query(60, ge=1, le=1440, description="Lookback window in minutes"),
    limit: int = Query(200, ge=1, le=1000, description="Max number of events to return"),
    log_group: str = Query(LOG_GROUP_DEFAULT, description="CloudWatch Logs log group name"),
    region: str = Query("us-east-1", description="AWS region"),
) -> Dict[str, Any]:
    raw_events = fetch_log_events_json(
        log_group=log_group,
        minutes=minutes,
        limit=limit,
        region=region,
    )

    normalized: List[Dict[str, Any]] = []
    for r in raw_events:
        # Only autoscaling source (extra safety)
        if (r.get("source") or "") != "aws.autoscaling":
            continue
        normalized.append(normalize_autoscaling_event(r, default_region=region))

    # newest-first (timestamp is ISO string; good enough for Phase 8)
    normalized.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    return {
        "ok": True,
        "source": "cloudwatch_logs",
        "log_group": log_group,
        "region": region,
        "count": len(normalized),
        "events": normalized,
    }
