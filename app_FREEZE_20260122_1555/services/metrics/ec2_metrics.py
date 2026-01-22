import boto3
from datetime import datetime, timedelta, timezone


def fetch_ec2_metrics(instance_id: str, region: str = "us-east-1") -> dict:
    """
    Read-only EC2 metrics from CloudWatch.
    Safe: no alarms, no writes, no mutations.
    """
    cw = boto3.client("cloudwatch", region_name=region)

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=15)

    def _metric_series(name, unit=None):
        resp = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName=name,
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=60,
            Statistics=["Sum"],
            Unit=unit,
        )

        points = resp.get("Datapoints", [])
        points.sort(key=lambda x: x["Timestamp"])

        return [
            {
                "timestamp": p["Timestamp"].isoformat(),
                "value": int(p["Sum"]),
            }
            for p in points
        ]

    def _cpu_latest():
        resp = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=["Average"],
            Unit="Percent",
        )
        pts = resp.get("Datapoints", [])
        if not pts:
            return None
        return round(sorted(pts, key=lambda x: x["Timestamp"])[-1]["Average"], 2)

    return {
        "window_minutes": 15,
        "cpu_percent": _cpu_latest(),
        "network_in_bytes": _metric_series("NetworkIn", "Bytes"),
        "network_out_bytes": _metric_series("NetworkOut", "Bytes"),
    }
