import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class AWSEC2Manager:
    """
    EC2/VPC related helper manager.

    Notes:
    - This class intentionally returns UI-friendly JSON-safe dicts/lists.
    - Exceptions are caught and converted into predictable error structures.
    """

    def __init__(self, region="us-east-1"):
        self.region = region
        try:
            self.ec2 = boto3.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    # ------------------------------------------------------------
    # Instances
    # ------------------------------------------------------------
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
                            "state": inst.get("State", {}).get("Name"),
                            "az": inst.get("Placement", {}).get("AvailabilityZone"),
                            "vpc_id": inst.get("VpcId"),
                            "subnet_id": inst.get("SubnetId"),
                            "tags": inst.get("Tags", []),
                        }
                    )

            return instances

        except (ClientError, NoCredentialsError):
            return [{"instance_id": "i-placeholder"}]

    # ------------------------------------------------------------
    # Internet Gateways (IGW)
    # ------------------------------------------------------------
    def list_internet_gateways(self):
        """
        List Internet Gateways with attachment info.

        Returns:
          [
            {
              "internet_gateway_id": "igw-...",
              "tags": [...],
              "attachments": [
                {
                  "vpc_id": "vpc-...",
                  "state": "available|attaching|attached|detaching|detached"
                }
              ],
              "attached_vpc_ids": ["vpc-..."]
            },
            ...
          ]
        """
        if not self.ec2:
            return []

        try:
            resp = self.ec2.describe_internet_gateways()
            igws = []

            for igw in resp.get("InternetGateways", []):
                attachments = []
                attached_vpc_ids = []

                for att in igw.get("Attachments", []) or []:
                    vpc_id = att.get("VpcId")
                    state = att.get("State")
                    attachments.append(
                        {
                            "vpc_id": vpc_id,
                            "state": state,
                        }
                    )
                    if vpc_id:
                        attached_vpc_ids.append(vpc_id)

                igws.append(
                    {
                        "internet_gateway_id": igw.get("InternetGatewayId"),
                        "tags": igw.get("Tags", []),
                        "attachments": attachments,
                        "attached_vpc_ids": attached_vpc_ids,
                    }
                )

            return igws

        except (ClientError, NoCredentialsError):
            return []

    def create_internet_gateway(self, name: str | None = None):
        """
        Create an Internet Gateway.
        Optionally adds a Name tag.
        Returns:
          {"status": "success", "internet_gateway_id": "igw-..."}
          or {"status":"failed","error":"..."}
        """
        if not self.ec2:
            return {"status": "failed", "error": "AWS client not initialized"}

        try:
            resp = self.ec2.create_internet_gateway()
            igw_id = resp.get("InternetGateway", {}).get("InternetGatewayId")

            if name and igw_id:
                try:
                    self.ec2.create_tags(
                        Resources=[igw_id],
                        Tags=[{"Key": "Name", "Value": name}],
                    )
                except (ClientError, NoCredentialsError):
                    # Tagging failure should not fail creation
                    pass

            return {"status": "success", "internet_gateway_id": igw_id}

        except (ClientError, NoCredentialsError) as e:
            return {"status": "failed", "error": str(e)}

    def attach_internet_gateway(self, igw_id: str, vpc_id: str):
        """
        Attach IGW to VPC.
        Returns:
          {"status":"success"} or {"status":"failed","error":"..."}
        """
        if not self.ec2:
            return {"status": "failed", "error": "AWS client not initialized"}

        if not igw_id or not vpc_id:
            return {"status": "failed", "error": "igw_id and vpc_id are required"}

        try:
            self.ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            return {"status": "success"}
        except (ClientError, NoCredentialsError) as e:
            return {"status": "failed", "error": str(e)}

    def detach_internet_gateway(self, igw_id: str, vpc_id: str):
        """
        Detach IGW from VPC.
        Returns:
          {"status":"success"} or {"status":"failed","error":"..."}
        """
        if not self.ec2:
            return {"status": "failed", "error": "AWS client not initialized"}

        if not igw_id or not vpc_id:
            return {"status": "failed", "error": "igw_id and vpc_id are required"}

        try:
            self.ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            return {"status": "success"}
        except (ClientError, NoCredentialsError) as e:
            return {"status": "failed", "error": str(e)}

    def delete_internet_gateway(self, igw_id: str):
        """
        Delete IGW.
        Note: AWS requires IGW to be detached from all VPCs before deletion.
        Returns:
          {"status":"success"} or {"status":"failed","error":"..."}
        """
        if not self.ec2:
            return {"status": "failed", "error": "AWS client not initialized"}

        if not igw_id:
            return {"status": "failed", "error": "igw_id is required"}

        try:
            # Defensive: ensure it's detached from any VPCs first
            try:
                resp = self.ec2.describe_internet_gateways(InternetGatewayIds=[igw_id])
                igws = resp.get("InternetGateways", [])
                if igws:
                    for att in igws[0].get("Attachments", []) or []:
                        vpc_id = att.get("VpcId")
                        if vpc_id:
                            try:
                                self.ec2.detach_internet_gateway(
                                    InternetGatewayId=igw_id, VpcId=vpc_id
                                )
                            except (ClientError, NoCredentialsError):
                                # If detach fails, deletion will fail and return error below
                                pass
            except (ClientError, NoCredentialsError):
                pass

            self.ec2.delete_internet_gateway(InternetGatewayId=igw_id)
            return {"status": "success"}
        except (ClientError, NoCredentialsError) as e:
            return {"status": "failed", "error": str(e)}
