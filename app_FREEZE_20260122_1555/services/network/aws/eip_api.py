"""
AWS Elastic IP (EIP) Automation Module for NetPilot AI.

Provides helpers for:
- Listing Elastic IPs
"""

import boto3
from typing import List, Dict

class ElasticIPManager:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ec2 = boto3.client("ec2", region_name=region)

    def list_eips(self) -> List[Dict]:
        """
        List all allocated Elastic IPs.
        """
        response = self.ec2.describe_addresses()
        return response.get("Addresses", [])
