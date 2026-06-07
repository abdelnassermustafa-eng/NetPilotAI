from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import time

router = APIRouter(prefix="/api/v1", tags=["terminal"])


class ExecuteRequest(BaseModel):
    command: str


class ExecuteResponse(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int


@router.post("/execute", response_model=ExecuteResponse)
def execute_command(payload: ExecuteRequest):
    cmd = payload.command.strip()

    if not cmd:
        raise HTTPException(status_code=400, detail="Empty command")

    start = time.time()

    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    duration_ms = int((time.time() - start) * 1000)

    return ExecuteResponse(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration_ms=duration_ms,
    )
