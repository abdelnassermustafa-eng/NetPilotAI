"""
Check Point Management API Module for NetPilot AI.

This module interacts with the Check Point Management Server (via SmartConsole API).

Future Enhancements:
- Authentication handling
- Object management (hosts, networks, services)
- Policy retrieval and modification
- Publish and install policy functionality
"""

import httpx
from typing import Optional

class CheckPointClient:
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session_id: Optional[str] = None

    async def login(self):
        """
        Authenticate to Check Point Management API.
        """
        url = f"https://{self.host}/web_api/login"
        payload = {"user": self.username, "password": self.password}

        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            self.session_id = response.json().get("sid")

        return self.session_id

    async def show_hosts(self):
        """
        Retrieve all host objects.
        """
        if not self.session_id:
            raise RuntimeError("You must log in first.")

        url = f"https://{self.host}/web_api/show-hosts"
        headers = {"X-chkp-sid": self.session_id}

        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            return response.json()
