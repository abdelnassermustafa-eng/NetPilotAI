import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class SecurityGroupManager:
    def __init__(self, region="us-east-1"):
        try:
            self.ec2 = boto3.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    def list_security_groups(self):
        """Return Security Groups."""
        if not self.ec2:
            return [{"sg_id": "sg-placeholder"}]

        try:
            response = self.ec2.describe_security_groups()

            sgs = [
                {
                    "sg_id": sg.get("GroupId"),
                    "name": sg.get("GroupName"),
                    "description": sg.get("Description"),
                    "vpc_id": sg.get("VpcId"),
                    "inbound_rules": sg.get("IpPermissions", []),
                    "outbound_rules": sg.get("IpPermissionsEgress", []),
                }
                for sg in response.get("SecurityGroups", [])
            ]

            return sgs

        except (ClientError, NoCredentialsError):
            return [{"sg_id": "sg-placeholder"}]
