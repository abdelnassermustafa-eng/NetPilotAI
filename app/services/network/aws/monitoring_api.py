"""
AWS CloudWatch Monitoring Module for NetPilot AI.

Provides helpers for:
- Fetching basic metrics (e.g., CPUUtilization) for EC2 instances
"""

import boto3
from datetime import datetime, timedelta
from typing import List, Dict

class CloudWatchMonitor:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)

    def get_ec2_cpu_utilization(
        self,
        instance_id: str,
        period: int = 300,
        minutes: int = 60
    ) -> List[Dict]:
        """
        Retrieve CPUUtilization metrics for an EC2 instance.
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)

        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[
                {"Name": "InstanceId", "Value": instance_id}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=["Average"]
        )

        return response.get("Datapoints", [])
