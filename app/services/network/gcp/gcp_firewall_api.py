"""
Google Cloud Firewall Automation Module for NetPilot AI.

Future Enhancements:
- Create firewall rules
- Update/patch existing rules
- Cross-environment rule comparison
- Compliance and security audits
- Detection of shadowed or redundant rules
"""

from google.cloud import compute_v1

class GCPFirewallManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.firewall_client = compute_v1.FirewallsClient()

    def list_firewall_rules(self):
        """
        List all firewall rules in the project.
        """
        return list(self.firewall_client.list(project=self.project_id))

    def list_firewall_rules_for_network(self, network_name: str):
        """
        List only the rules associated with a specific VPC network.
        network_name example: "global/networks/my-vpc"
        """
        all_rules = self.list_firewall_rules()
        return [rule for rule in all_rules if rule.network.endswith(network_name)]
