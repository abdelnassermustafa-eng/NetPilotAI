import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class AWSInternetGatewayManager:
    def __init__(self, region: str = "us-east-1"):
        try:
            session = boto3.session.Session()
            self.ec2 = session.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    # ---------------------------------------------------------
    # CREATE INTERNET GATEWAY
    # ---------------------------------------------------------
    def create_igw(self, name: str = None):
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
            }

        except ClientError as e:
            return {"status": "failed", "error": e.response["Error"]["Message"]}

    # ---------------------------------------------------------
    # ATTACH IGW TO VPC
    # ---------------------------------------------------------
    def attach_igw(self, igw_id: str, vpc_id: str):
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
        try:
            response = self.ec2.describe_internet_gateways()
            igws = []

            for igw in response["InternetGateways"]:
                attachments = []
                for att in igw.get("Attachments", []):
                    attachments.append(
                        {
                            "vpc_id": att.get("VpcId"),
                            "state": att.get("State"),
                        }
                    )

                igws.append(
                    {
                        "internet_gateway_id": igw["InternetGatewayId"],
                        "attachments": attachments,
                        "tags": {
                            t["Key"]: t["Value"]
                            for t in igw.get("Tags", [])
                        },
                    }
                )

            return {"status": "success", "internet_gateways": igws}

        except (ClientError, NoCredentialsError):
            return {"status": "failed", "internet_gateways": []}

