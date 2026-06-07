"""
Google Cloud NAT Automation Module for NetPilot AI.

Future Enhancements:
- Create Cloud NAT gateways
- Configure NAT IP pools
- Auto-attach NAT to Cloud Routers
- Autoscaling based on traffic/load
- Multi-region NAT architecture automation
"""

from google.cloud import compute_v1

class GCPCloudNATManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.nat_client = compute_v1.RoutersClient()

    def list_nat_gateways(self, region: str, router_name: str):
        """
        List all configured NAT gateways on a Cloud Router.
        """
        router = self.nat_client.get(
            project=self.project_id,
            region=region,
            router=router_name
        )
        return router.nats or []

    def list_nat_ip_ranges(self, region: str, router_name: str):
        """
        List NAT IP allocations associated with a NAT gateway.
        """
        nats = self.list_nat_gateways(region, router_name)
        ip_ranges = []
        for nat in nats:
            ip_ranges.extend(nat.source_subnetwork_ip_ranges_to_nat or [])
        return ip_ranges
