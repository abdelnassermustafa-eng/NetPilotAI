import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class AWSInternetGatewayManager:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        try:
            session = boto3.session.Session()
            self.ec2 = session.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    # ---------------------------------------------------------
    # INTERNAL GUARD
    # ---------------------------------------------------------
    def _ensure_client(self):
        if not self.ec2:
            return {
                "status": "failed",
                "error": "AWS EC2 client not initialized. Check credentials and region.",
            }
        return None

    # ---------------------------------------------------------
    # CREATE INTERNET GATEWAY
    # ---------------------------------------------------------
    def create_igw(self, name: str = None):
        guard = self._ensure_client()
        if guard:
            return guard

        try:
            response = self.ec2.create_internet_gateway()
            igw_id = response["InternetGateway"]["InternetGatewayId"]

            if name:
                self.ec2.create_tags(
                    Resources=[igw_id],
                    Tags=[{"Key": "Name", "Value": name}],
                )

            return {
                "status": "success",
                "internet_gateway_id": igw_id,
                "region": self.region,
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # ATTACH IGW TO VPC
    # ---------------------------------------------------------
    def attach_igw(self, igw_id: str, vpc_id: str):
        guard = self._ensure_client()
        if guard:
            return guard

        try:
            self.ec2.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id,
            )
            return {
                "status": "success",
                "internet_gateway_id": igw_id,
                "vpc_id": vpc_id,
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # DETACH IGW FROM VPC
    # ---------------------------------------------------------
    def detach_igw(self, igw_id: str, vpc_id: str):
        guard = self._ensure_client()
        if guard:
            return guard

        try:
            self.ec2.detach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id,
            )
            return {
                "status": "success",
                "internet_gateway_id": igw_id,
                "vpc_id": vpc_id,
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # DELETE INTERNET GATEWAY
    # ---------------------------------------------------------
    def delete_igw(self, igw_id: str):
        guard = self._ensure_client()
        if guard:
            return guard

        try:
            self.ec2.delete_internet_gateway(
                InternetGatewayId=igw_id
            )
            return {
                "status": "success",
                "internet_gateway_id": igw_id,
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # LIST INTERNET GATEWAYS
    # ---------------------------------------------------------
    def list_igws(self):
        guard = self._ensure_client()
        if guard:
            return guard

        try:
            response = self.ec2.describe_internet_gateways()
            igws = []

            for igw in response.get("InternetGateways", []):
                tags = {
                    t["Key"]: t["Value"]
                    for t in igw.get("Tags", [])
                }

                attachment = igw.get("Attachments", [])
                attached_vpc_id = (
                    attachment[0]["VpcId"] if attachment else None
                )

                igws.append(
                    {
                        "internet_gateway_id": igw["InternetGatewayId"],
                        "name": tags.get("Name"),
                        "attached_vpc_id": attached_vpc_id,
                        "attachments": attachment,
                        "tags": tags,
                    }
                )

            return {
                "status": "success",
                "region": self.region,
                "internet_gateways": igws,
            }

        except NoCredentialsError:
            return {
                "status": "failed",
                "error": "AWS credentials not found.",
                "internet_gateways": [],
            }

        except ClientError as e:
            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
                "internet_gateways": [],
            }

