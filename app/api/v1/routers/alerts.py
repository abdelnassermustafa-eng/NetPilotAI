from fastapi import APIRouter
from datetime import datetime
import boto3
import os

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ==================================================
# Phase 7.2 — Normalized alert schema (canonical)
# ==================================================
def normalize_alert(
    *,
    alert_id: str,
    name: str,
    state: str,
    severity: str = "info",
    source: str,
    updated_at: str | None = None,
    description: str | None = None,
) -> dict:
    return {
        "id": alert_id,
        "name": name,
        "state": state,
        "severity": severity,
        "source": source,
        "updated_at": updated_at or datetime.utcnow().isoformat() + "Z",
        "description": description,
    }


# ==================================================
# Phase 7.1 — Read-only CloudWatch alerts endpoint
# ==================================================
@router.get("/cloudwatch")
def list_cloudwatch_alarms():
    """
    Read-only CloudWatch alarms listing.
    Safe: no create/update/delete.
    Normalized schema (Phase 7.2).
    """

    # -----------------------------
    # Local-dev safe fallback
    # -----------------------------
    if os.getenv("AWS_EXECUTION_ENV") is None:
        alarms = [
            normalize_alert(
                alert_id="local-unhealthy-targets",
                name="Unhealthy Targets",
                state="OK",
                severity="warning",
                source="local-dev",
                description="No unhealthy targets detected",
            ),
            normalize_alert(
                alert_id="local-billing-threshold",
                name="Billing Threshold",
                state="OK",
                severity="info",
                source="local-dev",
                description="Billing within expected range",
            ),
        ]

        return {
            "status": "ok",
            "source": "local-dev",
            "count": len(alarms),
            "alarms": alarms,
        }

    # -----------------------------
    # AWS CloudWatch (read-only)
    # -----------------------------
    try:
        cw = boto3.client("cloudwatch")
        response = cw.describe_alarms()

        alarms = []
        for a in response.get("MetricAlarms", []):
            alarms.append(
                normalize_alert(
                    alert_id=a.get("AlarmArn", a.get("AlarmName")),
                    name=a.get("AlarmName"),
                    state=a.get("StateValue"),
                    severity="critical" if a.get("StateValue") == "ALARM" else "info",
                    source="cloudwatch",
                    updated_at=a.get("StateUpdatedTimestamp").isoformat() + "Z"
                    if a.get("StateUpdatedTimestamp")
                    else None,
                    description=a.get("AlarmDescription"),
                )
            )

        return {
            "status": "ok",
            "source": "cloudwatch",
            "count": len(alarms),
            "alarms": alarms,
        }

    except Exception as exc:
        # Never break UI
        return {
            "status": "error",
            "source": "cloudwatch",
            "error": str(exc),
            "alarms": [],
        }
