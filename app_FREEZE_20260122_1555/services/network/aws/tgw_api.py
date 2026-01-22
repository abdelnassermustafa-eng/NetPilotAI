"""
AWS Transit Gateway Automation Module for NetPilot AI.

Future Enhancements:
- Create Transit Gateway
- Create TGW attachments (VPCs)
- Manage TGW route tables
"""

import boto3

class TransitGatewayManager:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ec2 = boto3.client("ec2", region_name=region)

    def list_transit_gateways(self):
        """
        List all Transit Gateways in the region.
        """
        response = self.ec2.describe_transit_gateways()
        return response.get("TransitGateways", [])

    def list_tgw_attachments(self, tgw_id: str):
        """
        List all attachments for a specific Transit Gateway.
        """
        response = self.ec2.describe_transit_gateway_attachments(
            Filters=[{"Name": "transit-gateway-id", "Values": [tgw_id]}]
        )
        return response.get("TransitGatewayAttachments", [])
