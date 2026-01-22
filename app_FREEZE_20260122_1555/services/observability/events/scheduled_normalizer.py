from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _iso(ts: Any) -> str:
    if isinstance(ts, str) and ts:
        return ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
    return datetime.now(timezone.utc).isoformat()


def normalize_scheduled_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    rule_arn = ""
    resources = raw.get("resources") or []
    if resources:
        rule_arn = resources[0]

    return {
        "source": "scheduled",
        "event_type": "scheduled_event",
        "severity": "info",
        "timestamp": _iso(raw.get("time")),
        "account_id": raw.get("account"),
        "region": raw.get("region"),
        "resource_id": rule_arn or "scheduled-rule",
        "rule_arn": rule_arn or None,
        "message": "Scheduled Event triggered",
        "raw": raw,
    }
