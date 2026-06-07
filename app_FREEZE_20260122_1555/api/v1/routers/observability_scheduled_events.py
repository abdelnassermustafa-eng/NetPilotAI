from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Query

from app.services.observability.events.cloudwatch_logs_reader import fetch_log_events_json
from app.services.observability.events.scheduled_normalizer import normalize_scheduled_event

router = APIRouter(
    prefix="/api/v1/observability/scheduled",
    tags=["Observability - Scheduled Events"],
)

LOG_GROUP_DEFAULT = "/aws/events/netpilot-autoscaling"


@router.get("/events")
def get_scheduled_events(
    minutes: int = Query(120, ge=1, le=1440),
    limit: int = Query(200, ge=1, le=1000),
    log_group: str = Query(LOG_GROUP_DEFAULT),
    region: str = Query("us-east-1"),
) -> Dict[str, Any]:
    raw_events = fetch_log_events_json(
        log_group=log_group,
        minutes=minutes,
        limit=limit,
        region=region,
    )

    events: List[Dict[str, Any]] = []
    for r in raw_events:
        if (r.get("source") or "") == "aws.events" and r.get("detail-type") == "Scheduled Event":
            events.append(normalize_scheduled_event(r))

    events.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    return {
        "ok": True,
        "source": "cloudwatch_logs",
        "count": len(events),
        "events": events,
    }
