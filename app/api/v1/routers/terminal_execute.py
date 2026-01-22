from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["terminal"])

class ExecuteRequest(BaseModel):
    command: str

@router.post("/execute")
def execute_command(req: ExecuteRequest):
    """
    Minimal execution stub.
    Restored to re-enable Terminal stability.
    """
    return {
        "stdout": f"Command received: {req.command}",
        "stderr": "",
        "exit_code": 0
    }
