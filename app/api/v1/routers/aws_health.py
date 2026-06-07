from fastapi import APIRouter
import boto3
from botocore.exceptions import BotoCoreError, ClientError

router = APIRouter(
    prefix="/aws/health",
    tags=["AWS Health"],
)

@router.get("")
async def aws_health_check():
    """
    Current AWS health check.
    Safe: uses sts:GetCallerIdentity only.
    """
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()

        return {
            "status": "ok",
            "account_id": identity.get("Account"),
            "arn": identity.get("Arn"),
            "user_id": identity.get("UserId"),
        }

    except (BotoCoreError, ClientError) as e:
        return {
            "status": "failed",
            "error": str(e),
        }
