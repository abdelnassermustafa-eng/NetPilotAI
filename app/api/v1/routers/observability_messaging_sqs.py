from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from app.services.observability.events.sqs_reader import fetch_sqs_messages
from app.services.observability.events.messaging_normalizer import normalize_sns_sqs_event

router = APIRouter(
    prefix="/api/v1/observability/messaging/sqs",
    tags=["Observability - Messaging (SQS)"],
)


@router.get("/events")
def get_messaging_events(
    queue_url: str = Query(..., description="SQS Queue URL"),
    limit: int = Query(10, ge=1, le=10),
    region: str = Query("us-east-1"),
) -> Dict[str, Any]:
    messages = fetch_sqs_messages(
        queue_url=queue_url,
        max_messages=limit,
        region=region,
    )

    events: List[Dict[str, Any]] = []

    for m in messages:
        body = m.get("Body")
        if not body:
            continue

        try:
            sns_envelope = json.loads(body)
        except Exception:
            continue

        if sns_envelope.get("Type") == "Notification":
            events.append(normalize_sns_sqs_event(sns_envelope))

    return {
        "ok": True,
        "source": "sqs",
        "queue_url": queue_url,
        "count": len(events),
        "events": events,
    }
