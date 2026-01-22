import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Query, Path
from typing import Optional
from fastapi import HTTPException
from fastapi import HTTPException, Query, Path


dynamodb = boto3.resource("dynamodb")
EVENTS_TABLE = os.getenv("EVENTS_TABLE", "netpilot_events")
table = dynamodb.Table(EVENTS_TABLE)

router = APIRouter(
    prefix="/observability/events",
    tags=["Observability / Events"],
)

@router.get("")
def list_events(
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    limit: int = Query(25, ge=1, le=100),
    cursor: Optional[str] = Query(None),
):
    """
    List events (read-only) from DynamoDB.
    """

    pk = f"ACCOUNT#{account_id}#REGION#{region}"

    query_args = {
        "KeyConditionExpression": Key("PK").eq(pk),
        "Limit": limit,
        "ScanIndexForward": False,  # newest first
    }

    if cursor:
        query_args["ExclusiveStartKey"] = json.loads(cursor)

    response = table.query(**query_args)

    return {
        "items": response.get("Items", []),
        "count": response.get("Count", 0),
        "next_cursor": (
            json.dumps(response["LastEvaluatedKey"])
            if "LastEvaluatedKey" in response
            else None
        ),
    }



@router.get("/{event_id}")
def get_event(
    event_id: str = Path(..., description="Event ID"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
):
    """
    Retrieve a single event by event_id (read-only).
    """

    pk = f"ACCOUNT#{account_id}#REGION#{region}"

    response = table.query(
        KeyConditionExpression=Key("PK").eq(pk),
        ScanIndexForward=False,
        Limit=100
    )

    for item in response.get("Items", []):
        if item.get("event_id") == event_id:
            return item

    raise HTTPException(status_code=404, detail="Event not found")


@router.get("/{event_id}")
def get_event(
    event_id: str = Path(..., description="Event ID"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
):
    """
    Retrieve a single event by event_id (read-only).
    """

    pk = f"ACCOUNT#{account_id}#REGION#{region}"

    response = table.query(
        KeyConditionExpression=Key("PK").eq(pk),
        ScanIndexForward=False,
        Limit=100
    )

    for item in response.get("Items", []):
        if item.get("event_id") == event_id:
            return item

    raise HTTPException(status_code=404, detail="Event not found")

