from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import boto3


def _to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def fetch_log_events_json(
    log_group: str,
    minutes: int = 60,
    limit: int = 200,
    region: str = "us-east-1",
) -> List[Dict[str, Any]]:
    """
    Read recent log events from a CloudWatch Logs log group and parse each event message as JSON.
    Assumes EventBridge -> Logs target is writing JSON strings.
    """
    client = boto3.client("logs", region_name=region)

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=max(1, minutes))

    events: List[Dict[str, Any]] = []
    next_token: Optional[str] = None

    # Use filter_log_events so we can control time window.
    while True:
        kwargs = {
            "logGroupName": log_group,
            "startTime": _to_ms(start),
            "endTime": _to_ms(end),
            "limit": min(10000, max(1, limit)),
        }
        if next_token:
            kwargs["nextToken"] = next_token

        resp = client.filter_log_events(**kwargs)

        for e in resp.get("events", []):
            msg = e.get("message", "")
            if not msg:
                continue
            try:
                payload = json.loads(msg)
                if isinstance(payload, dict):
                    events.append(payload)
            except Exception:
                # Non-JSON line; ignore safely
                continue

            if len(events) >= limit:
                return events

        nt = resp.get("nextToken")
        # Stop if no new token or token doesn't advance
        if not nt or nt == next_token:
            break
        next_token = nt

    return events
