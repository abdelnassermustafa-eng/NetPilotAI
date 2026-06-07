"""
Azure Virtual Network (VNet) Automation Module for NetPilot AI.

Future Enhancements:
- Create VNets
- Create Subnets
- Manage NSGs and route tables
- Configure VNet peering across regions/subscriptions
"""

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

class AzureVNetManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.client = NetworkManagementClient(self.credential, subscription_id)

    def list_vnets(self, resource_group: str):
        """
        List all virtual networks in the specified resource group.
        """
        return list(self.client.virtual_networks.list(resource_group))

    def list_subnets(self, resource_group: str, vnet_name: str):
        """
        List all subnets within a VNet.
        """
        return list(self.client.subnets.list(resource_group, vnet_name))
