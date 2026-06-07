"""
Juniper Mist Cloud Automation Module for NetPilot AI.

Mist is Juniper's AI-driven cloud platform for wireless, wired, and WAN.

Future Enhancements:
- Login with API token
- Organization inventory
- Site inventory
- Device inventory (APs, switches, gateways)
- Wireless SSID automation
"""

import httpx

class MistClient:
    def __init__(self, api_token: str, base_url: str = "https://api.mist.com/api/v1"):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

    async def get_organizations(self):
        """
        Retrieve all organizations linked to the API token.
        """
        url = f"{self.base_url}/self/orgs"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_sites(self, org_id: str):
        """
        Retrieve all sites for an organization.
        """
        url = f"{self.base_url}/orgs/{org_id}/sites"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
