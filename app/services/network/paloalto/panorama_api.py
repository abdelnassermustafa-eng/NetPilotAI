"""
Palo Alto Panorama Automation Module for NetPilot AI.

Panorama is used to manage Palo Alto firewalls centrally.
This module sets the foundation for API interactions.

Future Enhancements:
- Authentication with API key
- Device group and template retrieval
- Security policy automation
- Address/object creation
- Commit operations
"""

import httpx
from typing import Optional

class PanoramaClient:
    def __init__(self, host: str, api_key: Optional[str] = None, verify_ssl: bool = False):
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl

    async def get_api_key(self, username: str, password: str) -> str:
        """
        Retrieve API key using username/password.
        """
        url = f"https://{self.host}/api/?type=keygen&user={username}&password={password}"
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.get(url)
            response.raise_for_status()

            xml = response.text
            if "<key>" in xml:
                key = xml.split("<key>")[1].split("</key>")[0]
                self.api_key = key
                return key

            raise RuntimeError("Failed to retrieve Panorama API key.")

    async def get_device_groups(self):
        """
        Retrieve device groups.
        """
        if not self.api_key:
            raise RuntimeError("API key not set.")

        url = f"https://{self.host}/api/?type=config&action=get&xpath=/config/devices/entry/device-group&key={self.api_key}"
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text  # XML response
