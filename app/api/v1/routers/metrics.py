from fastapi import APIRouter
from app.services.metrics.runtime_metrics import get_runtime_metrics

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/summary")
def metrics_summary():
    """
    Phase 6.1 — runtime metrics (safe, read-only)
    """
    return {
        "status": "ok",
        "metrics": get_runtime_metrics(),
    }

