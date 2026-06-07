from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _iso(ts: Any) -> str:
    """
    EventBridge 'time' is usually an ISO string; CloudWatch may store it as string.
    Fall back to now if missing/unparseable.
    """
    if isinstance(ts, str) and ts:
        # Keep as-is if it looks ISO-ish; you can harden later.
        return ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
    return datetime.now(timezone.utc).isoformat()


def _severity(detail_type: str) -> str:
    dt = (detail_type or "").lower()
    if "unsuccessful" in dt or "failed" in dt:
        return "warning"
    return "info"


def _event_type(detail_type: str) -> str:
    dt = (detail_type or "").lower()
    if "launch" in dt:
        return "instance_launch"
    if "terminate" in dt:
        return "instance_terminate"
    if "refresh" in dt:
        return "refresh"
    if "group state change" in dt:
        return "group_state"
    return "autoscaling_event"


def normalize_autoscaling_event(raw: Dict[str, Any], default_region: str = "us-east-1") -> Dict[str, Any]:
    """
    Normalize a single EventBridge autoscaling event payload into NetPilot schema.
    Expected raw shape is EventBridge event:
      { "source": "aws.autoscaling", "detail-type": "...", "time": "...", "account": "...", "region": "...", "detail": {...} }
    """
    detail = raw.get("detail") or {}

    detail_type = raw.get("detail-type") or ""
    account_id = raw.get("account") or ""
    region = raw.get("region") or default_region

    asg_name = (
        detail.get("AutoScalingGroupName")
        or detail.get("autoScalingGroupName")
        or detail.get("AutoScalingGroup")
        or ""
    )

    instance_id = (
        detail.get("EC2InstanceId")
        or detail.get("EC2InstanceID")
        or detail.get("InstanceId")
        or detail.get("instanceId")
        or ""
    )

    az = (
        detail.get("AvailabilityZone")
        or detail.get("availabilityZone")
        or detail.get("Details", {}).get("Availability Zone")
        or ""
    )


    status = "success"
    dt_lower = (detail_type or "").lower()
    if "unsuccessful" in dt_lower or "failed" in dt_lower:
        status = "failed"

    message = (
        detail.get("Description")
        or detail.get("description")
        or detail.get("Cause")
        or detail_type
        or "Auto Scaling event"
    )


    normalized = {
        "source": "autoscaling",
        "event_type": _event_type(detail_type),
        "severity": _severity(detail_type),
        "timestamp": _iso(raw.get("time")),
        "account_id": account_id,
        "region": region,
        "resource_id": asg_name or "unknown-asg",
        "asg_name": asg_name or None,
        "instance_id": instance_id or None,
        "availability_zone": az or None,
        "status": status,
        "message": message,
        "raw": raw,
    }

    return normalized
