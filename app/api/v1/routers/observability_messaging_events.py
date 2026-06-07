from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from app.services.observability.events.cloudwatch_logs_reader import fetch_log_events_json
from app.services.observability.events.messaging_normalizer import normalize_sns_sqs_event

router = APIRouter(
    prefix="/api/v1/observability/messaging",
    tags=["Observability - Messaging"],
)

LOG_GROUP_DEFAULT = "/aws/events/netpilot-autoscaling"


@router.get("/events")
def get_messaging_events(
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
        # SNS via SQS events appear as aws.sns or embedded SNS envelopes
        if (r.get("Type") == "Notification") and ("TopicArn" in r):
            events.append(normalize_sns_sqs_event(r))

    events.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    return {
        "ok": True,
        "source": "cloudwatch_logs",
        "count": len(events),
        "events": events,
    }
