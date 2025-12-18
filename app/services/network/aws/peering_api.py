"""
AWS VPC Peering Automation Module for NetPilot AI.

Provides helpers for:
- Listing VPC peering connections
"""

import boto3
from typing import List, Dict

class VpcPeeringManager:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ec2 = boto3.client("ec2", region_name=region)

    def list_vpc_peerings(self) -> List[Dict]:
        """
        List all VPC peering connections in the region.
        """
        response = self.ec2.describe_vpc_peering_connections()
        return response.get("VpcPeeringConnections", [])
