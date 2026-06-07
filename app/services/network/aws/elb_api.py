"""
AWS Load Balancer (ALB/NLB) Automation Module for NetPilot AI.

Provides helpers for:
- Listing load balancers
- Listing target groups
"""

import boto3
from typing import List, Dict

class LoadBalancerManager:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.elbv2 = boto3.client("elbv2", region_name=region)

    def list_load_balancers(self) -> List[Dict]:
        """
        List all Application/Network Load Balancers.
        """
        response = self.elbv2.describe_load_balancers()
        return response.get("LoadBalancers", [])

    def list_target_groups(self) -> List[Dict]:
        """
        List all target groups.
        """
        response = self.elbv2.describe_target_groups()
        return response.get("TargetGroups", [])
