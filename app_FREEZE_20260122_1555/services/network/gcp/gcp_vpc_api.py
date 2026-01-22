"""
Google Cloud VPC Automation Module for NetPilot AI.

Future Enhancements:
- Create VPC networks
- Create subnets (regional)
- Manage firewall rules
- Configure VPC peering
- Shared VPC and host project automation
"""

from google.cloud import compute_v1

class GCPVPCManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.network_client = compute_v1.NetworksClient()
        self.subnet_client = compute_v1.SubnetworksClient()

    def list_vpcs(self):
        """
        List all VPC networks in the project.
        """
        return list(self.network_client.list(project=self.project_id))

    def list_subnets(self, region: str):
        """
        List all subnets in a specific region.
        """
        return list(self.subnet_client.list(project=self.project_id, region=region))
