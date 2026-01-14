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
        body = m.get("Body")  # ALWAYS bind first
        if not body:
            continue

        # Try to parse as JSON (SNS envelope)
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = None

        # Case 1: SNS → SQS
        if isinstance(parsed, dict) and parsed.get("Type") == "Notification":
            events.append(normalize_sns_sqs_event(parsed))
            continue

        # Case 2: Direct SQS message
        events.append(
            normalize_sns_sqs_event(
                {
                    "Body": body,
                    "MessageId": m.get("MessageId"),
                }
            )
        )


    return {
        "ok": True,
        "source": "sqs",
        "queue_url": queue_url,
        "count": len(events),
        "events": events,
    }

    body = m.get("Body")
