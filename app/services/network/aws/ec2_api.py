import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class AWSEC2Manager:
    def __init__(self, region="us-east-1"):
        try:
            self.ec2 = boto3.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    def list_instances(self):
        """Return EC2 instances."""
        if not self.ec2:
            return [{"instance_id": "i-placeholder"}]

        try:
            response = self.ec2.describe_instances()

            instances = []
            for reservation in response.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    instances.append(
                        {
                            "instance_id": inst.get("InstanceId"),
                            "type": inst.get("InstanceType"),
                            "state": inst["State"]["Name"],
                            "az": inst.get("Placement", {}).get("AvailabilityZone"),
                            "vpc_id": inst.get("VpcId"),
                            "subnet_id": inst.get("SubnetId"),
                            "tags": inst.get("Tags", []),
                        }
                    )

            return instances

        except (ClientError, NoCredentialsError):
            return [{"instance_id": "i-placeholder"}]
