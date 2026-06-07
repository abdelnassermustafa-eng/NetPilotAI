from fastapi import APIRouter
from app.services.metrics.runtime_metrics import get_runtime_metrics
from app.services.metrics.ec2_metrics import fetch_ec2_metrics
import os

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/summary")
def metrics_summary():
    """
    Phase 6.1 — Runtime + basic EC2 metrics (read-only).
    Safe aggregation layer for UI consumption.
    """

    runtime = get_runtime_metrics()

    instance_id = os.getenv("EC2_INSTANCE_ID")
    region = os.getenv("AWS_REGION", "us-east-1")

    ec2_metrics = {}
    if instance_id:
        try:
            ec2_metrics = fetch_ec2_metrics(instance_id, region)
        except Exception:
            ec2_metrics = {}

    return {
        "status": "ok",
        "metrics": {
            **runtime,
            **ec2_metrics,
        },
    }
