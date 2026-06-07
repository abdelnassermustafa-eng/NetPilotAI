from fastapi import APIRouter

router = APIRouter(
    prefix="/aws/health/legacy",
    tags=["AWS Health (Legacy)"],
)

@router.get("")
async def aws_health_legacy():
    """
    Legacy AWS health endpoint.
    Reserved for old implementation visibility.
    """

    return {
        "status": "unknown",
        "message": "Legacy AWS health not yet wired",
        "note": "This endpoint is reserved for the old implementation"
    }
