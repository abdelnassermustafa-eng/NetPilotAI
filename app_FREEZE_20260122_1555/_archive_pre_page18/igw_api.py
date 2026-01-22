import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, List, Any


class AWSInternetGatewayManager:
    def __init__(self, region: str = "us-east-1"):
        """
        Manager for AWS Internet Gateways.
        """
        try:
            session = boto3.session.Session()
            self.ec2 = session.client("ec2", region_name=region)
            self.ec2_resource = session.resource("ec2", region_name=region)
        except Exception:
            # In local/dev without AWS creds, gracefully degrade
            self.ec2 = None
            self.ec2_resource = None

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _placeholder_response(self) -> Dict[str, Any]:
        """
        Fallback used when there is no EC2 client (no credentials / offline).
        """
        return {
            "count": 1,
            "internet_gateways": [
                {
                    "igw_id": "igw-placeholder",
                    "attached_vpcs": ["vpc-placeholder"],
                    "state": "unknown",
                    "tags": [{"Key": "Name", "Value": "NetPilot-IGW-Placeholder"}],
                }
            ],
        }

    # ------------------------------------------------------------------
    # LIST INTERNET GATEWAYS
    # ------------------------------------------------------------------
    def list_internet_gateways(self) -> Dict[str, Any]:
        """
        Return all Internet Gateways in the region.
        """
        if not self.ec2:
            return self._placeholder_response()

        try:
            response = self.ec2.describe_internet_gateways()
            igws: List[Dict[str, Any]] = []

            for igw in response.get("InternetGateways", []):
                igw_id = igw.get("InternetGatewayId")
                attachments = igw.get("Attachments", [])
                tags = igw.get("Tags", [])

                attached_vpcs = [
                    a.get("VpcId")
                    for a in attachments
                    if a.get("VpcId") is not None
                ]

                # Derive a simple "state" from attachments if present
                if attachments:
                    # Usually "available", "attaching", etc.
                    state = attachments[0].get("State", "unknown")
                else:
                    state = "detached"

                igws.append(
                    {
                        "igw_id": igw_id,
                        "attached_vpcs": attached_vpcs,
                        "state": state,
                        "tags": tags,
                    }
                )

            return {"count": len(igws), "internet_gateways": igws}

        except (ClientError, NoCredentialsError) as e:
            msg = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else str(e)
            )
            return {
                "status": "failed",
                "error": msg,
                "internet_gateways": [],
                "count": 0,
            }

    # ------------------------------------------------------------------
    # CREATE INTERNET GATEWAY
    # ------------------------------------------------------------------
    def create_internet_gateway(
        self, name: str | None = None, vpc_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Create a new Internet Gateway.
        Optionally:
          - tag it with a Name
          - immediately attach it to a given VPC.
        """
        if not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 client not initialized (missing AWS credentials?).",
            }

        try:
            response = self.ec2.create_internet_gateway()
            igw = response.get("InternetGateway", {})
            igw_id = igw.get("InternetGatewayId")

            # Optional Name tag
            if name:
                try:
                    self.ec2.create_tags(
                        Resources=[igw_id],
                        Tags=[{"Key": "Name", "Value": name}],
                    )
                except ClientError:
                    # Tagging failure shouldn't block IGW creation
                    pass

            attach_result: Dict[str, Any] | None = None

            # Optional immediate attach
            if vpc_id:
                attach_result = self.attach_internet_gateway(igw_id, vpc_id)

            result: Dict[str, Any] = {
                "status": "created",
                "igw_id": igw_id,
                "attached_vpcs": [],
            }

            if attach_result and attach_result.get("status") == "success":
                result["attached_vpcs"] = [vpc_id]
                result["attach_status"] = "attached"
            elif attach_result and attach_result.get("status") == "failed":
                result["attach_status"] = "attach_failed"
                result["attach_error"] = attach_result.get("error")

            return result

        except ClientError as e:
            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
            }

    # ------------------------------------------------------------------
    # ATTACH INTERNET GATEWAY
    # ------------------------------------------------------------------
    def attach_internet_gateway(self, igw_id: str, vpc_id: str) -> Dict[str, Any]:
        """
        Attach an Internet Gateway to a VPC.
        """
        if not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 client not initialized (missing AWS credentials?).",
            }

        try:
            self.ec2.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id,
            )
            return {
                "status": "success",
                "igw_id": igw_id,
                "vpc_id": vpc_id,
                "action": "attached",
            }
        except ClientError as e:
            return {
                "status": "failed",
                "igw_id": igw_id,
                "vpc_id": vpc_id,
                "error": e.response["Error"]["Message"],
            }

    # ------------------------------------------------------------------
    # DETACH INTERNET GATEWAY
    # ------------------------------------------------------------------
    def detach_internet_gateway(self, igw_id: str, vpc_id: str) -> Dict[str, Any]:
        """
        Detach an Internet Gateway from a VPC.
        """
        if not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 client not initialized (missing AWS credentials?).",
            }

        try:
            self.ec2.detach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id,
            )
            return {
                "status": "success",
                "igw_id": igw_id,
                "vpc_id": vpc_id,
                "action": "detached",
            }
        except ClientError as e:
            return {
                "status": "failed",
                "igw_id": igw_id,
                "vpc_id": vpc_id,
                "error": e.response["Error"]["Message"],
            }

    # ------------------------------------------------------------------
    # DELETE INTERNET GATEWAY
    # ------------------------------------------------------------------
    def delete_internet_gateway(self, igw_id: str) -> Dict[str, Any]:
        """
        Delete an Internet Gateway.
        It must not be attached to any VPC.
        """
        if not self.ec2:
            return {
                "status": "failed",
                "error": "EC2 client not initialized (missing AWS credentials?).",
            }

        try:
            self.ec2.delete_internet_gateway(
                InternetGatewayId=igw_id,
            )
            return {
                "status": "success",
                "igw_id": igw_id,
                "action": "deleted",
            }
        except ClientError as e:
            return {
                "status": "failed",
                "igw_id": igw_id,
                "error": e.response["Error"]["Message"],
            }
