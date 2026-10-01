"""API client for Unofficial One Hungary."""

from __future__ import annotations

import aiohttp


class OneApiClient:
    """One Hungary API client."""

    BASE_URL = "https://www.one.hu"

    def __init__(self, session_cookie: str, csrf_token: str) -> None:
        self._session_cookie = session_cookie
        self._csrf_token = csrf_token

    async def get_services(self):
        """Return mobile services."""

        headers = {
            "X-CSRF-Token": self._csrf_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": self._session_cookie,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/o/ecare/services?serviceType=Mobile",
                headers=headers,
            ) as response:
                return await response.json()

    async def get_usage(self, msisdn: str):
        """Return usage data for a phone number."""
        raise NotImplementedError
