"""
Azure Network Security Group (NSG) Automation Module for NetPilot AI.

Future Enhancements:
- Create NSGs
- Add inbound/outbound rules
- Compare NSG rules across environments
- Automated compliance checks
- Cleanup unused or shadowed rules
"""

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

class AzureNSGManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.client = NetworkManagementClient(self.credential, subscription_id)

    def list_nsgs(self, resource_group: str):
        """
        List all NSGs in the specified resource group.
        """
        return list(self.client.network_security_groups.list(resource_group))

    def list_nsg_rules(self, resource_group: str, nsg_name: str):
        """
        Retrieve all rules from an NSG.
        """
        return list(self.client.security_rules.list(resource_group, nsg_name))
