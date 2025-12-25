import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Any, Dict, List, Optional


class AWSNatGatewayManager:
    """
    Manage AWS NAT Gateways for NetPilot.
    """

    def __init__(self, region: str = "us-east-1"):
        try:
            session = boto3.session.Session()
            self.ec2 = session.client("ec2", region_name=region)
        except Exception:
            self.ec2 = None

    # ------------------------------------------------------
    # Helpers
    # ------------------------------------------------------
    def _no_client(self) -> Dict[str, Any]:
        return {
            "status": "failed",
            "error": "EC2 client not initialized (missing AWS credentials?).",
        }

    # ------------------------------------------------------
    # LIST NAT GATEWAYS
    # ------------------------------------------------------
    def list_nat_gateways(self) -> Dict[str, Any]:
        """
        List all NAT Gateways in the region, with key details for UI.
        """
        if not self.ec2:
            return {
                "count": 1,
                "nat_gateways": [
                    {
                        "nat_gateway_id": "nat-placeholder",
                        "state": "unknown",
                        "subnet_id": "subnet-placeholder",
                        "vpc_id": "vpc-placeholder",
                        "public_ip": "0.0.0.0",
                        "allocation_id": "eipalloc-placeholder",
                    }
                ],
            }

        try:
            resp = self.ec2.describe_nat_gateways()
            items: List[Dict[str, Any]] = []

            for ngw in resp.get("NatGateways", []):
                nat_id = ngw.get("NatGatewayId")
                state = ngw.get("State", "unknown")
                subnet_id = ngw.get("SubnetId")
                vpc_id = ngw.get("VpcId")

                public_ip = None
                allocation_id = None

                addrs = ngw.get("NatGatewayAddresses", [])
                if addrs:
                    # Take the first address
                    addr0 = addrs[0]
                    public_ip = addr0.get("PublicIp")
                    allocation_id = addr0.get("AllocationId")

                items.append(
                    {
                        "nat_gateway_id": nat_id,
                        "state": state,
                        "subnet_id": subnet_id,
                        "vpc_id": vpc_id,
                        "public_ip": public_ip,
                        "allocation_id": allocation_id,
                    }
                )

            return {
                "count": len(items),
                "nat_gateways": items,
            }

        except (ClientError, NoCredentialsError) as e:
            msg = (
                e.response["Error"]["Message"]
                if isinstance(e, ClientError)
                else str(e)
            )
            return {"status": "failed", "error": msg, "count": 0, "nat_gateways": []}

    # ------------------------------------------------------
    # CREATE NAT GATEWAY (auto-allocate EIP)
    # ------------------------------------------------------
    def create_nat_gateway(
        self,
        subnet_id: str,
        name: Optional[str] = None,
        allocation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a NAT Gateway in the given subnet.
        If allocation_id is not provided, auto-allocate an Elastic IP (VPC).
        """
        if not self.ec2:
            return self._no_client()

        if not subnet_id:
            return {"status": "failed", "error": "subnet_id is required."}

        allocated_here = False
        eip_alloc_id: Optional[str] = allocation_id

        try:
            # Auto-allocate an EIP if not provided
            if not eip_alloc_id:
                eip_resp = self.ec2.allocate_address(Domain="vpc")
                eip_alloc_id = eip_resp.get("AllocationId")
                allocated_here = True

            create_resp = self.ec2.create_nat_gateway(
                SubnetId=subnet_id,
                AllocationId=eip_alloc_id,
            )
            nat = create_resp.get("NatGateway", {})
            nat_id = nat.get("NatGatewayId")
            state = nat.get("State", "pending")

            # Optional tag
            if name and nat_id:
                try:
                    self.ec2.create_tags(
                        Resources=[nat_id],
                        Tags=[{"Key": "Name", "Value": name}],
                    )
                except ClientError:
                    # Tagging failure shouldn't block NAT creation
                    pass

            return {
                "status": "created",
                "nat_gateway_id": nat_id,
                "state": state,
                "subnet_id": subnet_id,
                "allocation_id": eip_alloc_id,
                "eip_allocated_here": allocated_here,
            }

        except ClientError as e:
            # If we allocated an EIP in this method and creation failed,
            # we can attempt to release it to avoid leaks.
            if allocated_here and eip_alloc_id:
                try:
                    self.ec2.release_address(AllocationId=eip_alloc_id)
                except ClientError:
                    pass

            return {
                "status": "failed",
                "error": e.response["Error"]["Message"],
            }

    # ------------------------------------------------------
    # DELETE NAT GATEWAY (optionally release EIP)
    # ------------------------------------------------------
    def delete_nat_gateway(
        self, nat_gateway_id: str, release_eip: bool = True
    ) -> Dict[str, Any]:
        """
        Delete a NAT Gateway.
        Optionally also release its associated Elastic IP.
        """
        if not self.ec2:
            return self._no_client()

        if not nat_gateway_id:
            return {"status": "failed", "error": "nat_gateway_id is required."}

        allocation_id: Optional[str] = None

        try:
            # First, look up NAT to find allocation ID
            desc = self.ec2.describe_nat_gateways(
                Filters=[
                    {
                        "Name": "nat-gateway-id",
                        "Values": [nat_gateway_id],
                    }
                ]
            )
            gws = desc.get("NatGateways", [])
            if gws:
                addrs = gws[0].get("NatGatewayAddresses", [])
                if addrs:
                    allocation_id = addrs[0].get("AllocationId")

            # Delete NAT
            self.ec2.delete_nat_gateway(NatGatewayId=nat_gateway_id)

            # Optionally release EIP
            if release_eip and allocation_id:
                try:
                    self.ec2.release_address(AllocationId=allocation_id)
                except ClientError:
                    # Not critical; NAT delete is the main action.
                    pass

            return {
                "status": "success",
                "nat_gateway_id": nat_gateway_id,
                "allocation_id_released": allocation_id if release_eip else None,
            }

        except ClientError as e:
            return {
                "status": "failed",
                "nat_gateway_id": nat_gateway_id,
                "error": e.response["Error"]["Message"],
            }
