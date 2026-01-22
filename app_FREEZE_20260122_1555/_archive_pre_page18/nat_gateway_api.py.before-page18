import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class AWSNatGatewayManager:
    def __init__(self, region: str = "us-east-1"):
        try:
            session = boto3.session.Session()
            self.ec2 = session.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    # ---------------------------------------------------------
    # ALLOCATE ELASTIC IP
    # ---------------------------------------------------------
    def allocate_eip(self, name: str = None):
        try:
            response = self.ec2.allocate_address(Domain="vpc")
            allocation_id = response["AllocationId"]

            if name:
                self.ec2.create_tags(
                    Resources=[allocation_id],
                    Tags=[{"Key": "Name", "Value": name}],
                )

            return {
                "status": "success",
                "allocation_id": allocation_id,
                "public_ip": response.get("PublicIp"),
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # CREATE NAT GATEWAY
    # ---------------------------------------------------------
    def create_nat_gateway(
        self,
        subnet_id: str,
        allocation_id: str,
        name: str = None,
    ):
        try:
            response = self.ec2.create_nat_gateway(
                SubnetId=subnet_id,
                AllocationId=allocation_id,
            )

            nat_gw = response["NatGateway"]
            nat_gw_id = nat_gw["NatGatewayId"]

            if name:
                self.ec2.create_tags(
                    Resources=[nat_gw_id],
                    Tags=[{"Key": "Name", "Value": name}],
                )

            return {
                "status": "success",
                "nat_gateway_id": nat_gw_id,
                "subnet_id": subnet_id,
                "allocation_id": allocation_id,
                "state": nat_gw["State"],
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

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
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # RELEASE ELASTIC IP
    # ---------------------------------------------------------
    def release_eip(self, allocation_id: str):
        try:
            self.ec2.release_address(
                AllocationId=allocation_id
            )
            return {
                "status": "success",
                "allocation_id": allocation_id,
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # LIST NAT GATEWAYS
    # ---------------------------------------------------------
    def list_nat_gateways(self):
        try:
            response = self.ec2.describe_nat_gateways()
            nat_gateways = []

            for ngw in response["NatGateways"]:
                addresses = []
                for addr in ngw.get("NatGatewayAddresses", []):
                    addresses.append(
                        {
                            "allocation_id": addr.get("AllocationId"),
                            "public_ip": addr.get("PublicIp"),
                            "private_ip": addr.get("PrivateIp"),
                        }
                    )

                nat_gateways.append(
                    {
                        "nat_gateway_id": ngw["NatGatewayId"],
                        "subnet_id": ngw.get("SubnetId"),
                        "vpc_id": ngw.get("VpcId"),
                        "state": ngw["State"],
                        "addresses": addresses,
                        "create_time": str(ngw.get("CreateTime")),
                        "tags": {
                            t["Key"]: t["Value"]
                            for t in ngw.get("Tags", [])
                        },
                    }
                )

            return {"status": "success", "nat_gateways": nat_gateways}

        except (ClientError, NoCredentialsError):
            return {"status": "failed", "nat_gateways": []}
