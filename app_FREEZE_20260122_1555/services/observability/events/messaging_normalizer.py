from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict


def _iso(ts: Any) -> str:
    if isinstance(ts, str) and ts:
        return ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
    return datetime.now(timezone.utc).isoformat()


def normalize_sns_sqs_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an SNS message delivered via SQS.
    Expects raw to be the SNS envelope parsed from SQS Body.
    """
    message_str = raw.get("Message", "")
    try:
        message_payload = json.loads(message_str)
    except Exception:
        message_payload = {"raw_message": message_str}

    topic_arn = raw.get("TopicArn", "")
    message_id = raw.get("MessageId", "")

    return {
        "source": "messaging",
        "event_type": "sns_notification",
        "severity": "info",
        "timestamp": _iso(raw.get("Timestamp")),
        "account_id": topic_arn.split(":")[4] if topic_arn else None,
        "region": topic_arn.split(":")[3] if topic_arn else None,
        "resource_id": topic_arn or "sns-topic",
        "topic_arn": topic_arn,
        "message_id": message_id,
        "message": message_payload,
        "raw": raw,
    }
