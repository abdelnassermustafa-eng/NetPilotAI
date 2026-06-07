from __future__ import annotations

from typing import Any, Dict, List, Optional

import boto3


def fetch_sqs_messages(
    queue_url: str,
    max_messages: int = 10,
    wait_seconds: int = 2,
    region: str = "us-east-1",
) -> List[Dict[str, Any]]:
    """
    Read messages from SQS without deleting them.
    Safe for observability (no side effects).
    """
    client = boto3.client("sqs", region_name=region)

    resp = client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=min(10, max(1, max_messages)),
        WaitTimeSeconds=max(0, min(20, wait_seconds)),
        VisibilityTimeout=0,  # do NOT hide messages
        MessageAttributeNames=["All"],
        AttributeNames=["All"],
    )

    return resp.get("Messages", [])
