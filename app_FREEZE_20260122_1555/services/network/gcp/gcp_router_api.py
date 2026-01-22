"""
Google Cloud Router Automation Module for NetPilot AI.

Future Enhancements:
- Create Cloud Routers
- Configure BGP peers
- Automate hybrid VPN / Interconnect routing
- Dynamic routing policy orchestration
"""

from google.cloud import compute_v1

class GCPCloudRouterManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.router_client = compute_v1.RoutersClient()

    def list_routers(self, region: str):
        """
        List all Cloud Routers in a specific region.
        """
        return list(self.router_client.list(project=self.project_id, region=region))

    def list_bgp_peers(self, region: str, router_name: str):
        """
        List all BGP peers configured on a Cloud Router.
        """
        router = self.router_client.get(
            project=self.project_id, region=region, router=router_name
        )
        return router.bgp_peers or []

    def list_advertised_routes(self, region: str, router_name: str):
        """
        List BGP advertised routes learned or sent by the router.
        """
        return list(
            self.router_client.get_nat_ip_info(
                project=self.project_id,
                region=region,
                router=router_name
            )
        )
