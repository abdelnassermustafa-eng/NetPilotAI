import boto3
from botocore.exceptions import ClientError


class AWSNatGatewayManager:
    def __init__(self, region: str = "us-east-1"):
        session = boto3.session.Session()
        self.ec2 = session.client("ec2", region_name=region)

    # ---------------------------------------------------------
    # LIST NAT GATEWAYS
    # ---------------------------------------------------------
    def list_nat_gateways(self):
        try:
            response = self.ec2.describe_nat_gateways()
            nat_gateways = []

            for nat in response.get("NatGateways", []):
                nat_gateways.append({
                    "nat_gateway_id": nat.get("NatGatewayId"),
                    "subnet_id": nat.get("SubnetId"),
                    "vpc_id": nat.get("VpcId"),
                    "state": nat.get("State"),
                    "addresses": [
                        {
                            "allocation_id": addr.get("AllocationId"),
                            "public_ip": addr.get("PublicIp"),
                            "private_ip": addr.get("PrivateIp"),
                        }
                        for addr in nat.get("NatGatewayAddresses", [])
                    ],
                    "create_time": (
                        nat.get("CreateTime").isoformat()
                        if nat.get("CreateTime") else None
                    ),
                    "tags": {
                        t["Key"]: t["Value"]
                        for t in nat.get("Tags", [])
                    },
                })

            return {
                "status": "success",
                "nat_gateways": nat_gateways,
            }

        except ClientError as e:
            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
                "nat_gateways": [],
            }

    # ---------------------------------------------------------
    # CREATE NAT GATEWAY
    # ---------------------------------------------------------
    def create_nat_gateway(
        self,
        subnet_id: str,
        allocation_id: str | None = None,
        name: str | None = None,
    ):
        try:
            # Allocate Elastic IP if not provided
            if not allocation_id:
                eip = self.ec2.allocate_address(Domain="vpc")
                allocation_id = eip["AllocationId"]

            response = self.ec2.create_nat_gateway(
                SubnetId=subnet_id,
                AllocationId=allocation_id,
            )

            nat = response["NatGateway"]
            nat_id = nat["NatGatewayId"]

            if name:
                self.ec2.create_tags(
                    Resources=[nat_id],
                    Tags=[{"Key": "Name", "Value": name}],
                )

            return {
                "status": "success",
                "nat_gateway_id": nat_id,
                "subnet_id": subnet_id,
                "allocation_id": allocation_id,
                "state": nat.get("State"),
            }

        except ClientError as e:
            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
            }

    # ---------------------------------------------------------
    # DELETE NAT GATEWAY
    # ---------------------------------------------------------
    def delete_nat_gateway(self, nat_gateway_id: str):
        try:
            self.ec2.delete_nat_gateway(
                NatGatewayId=nat_gateway_id
            )

            return {
                "status": "success",
                "nat_gateway_id": nat_gateway_id,
            }

        except ClientError as e:
            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
            }
