"""API client for Unofficial One Hungary."""

from __future__ import annotations

from http.cookies import SimpleCookie
from typing import Any

import aiohttp


class OneApiError(Exception):
    """Base exception for One Hungary API errors."""


class OneApiAuthenticationError(OneApiError):
    """Authentication or session error."""


class OneApiClient:
    """One Hungary API client."""

    BASE_URL = "https://www.one.hu"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        cookie_header: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._cookie_header = cookie_header
        self._csrf_token = self._extract_csrf_token(cookie_header)

    @staticmethod
    def _extract_csrf_token(cookie_header: str) -> str:
        """Extract the CSRF token from the Cookie header."""
        cookies = SimpleCookie()
        cookies.load(cookie_header)

        csrf_cookie = cookies.get("CSRF_TOKEN")

        if csrf_cookie is None:
            raise OneApiAuthenticationError(
                "CSRF_TOKEN was not found in the Cookie header"
            )

        return csrf_cookie.value

    @property
    def _headers(self) -> dict[str, str]:
        """Return API request headers."""
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            "Cookie": self._cookie_header,
            "X-Csrf-Token": self._csrf_token,
        }

    async def get_services(self) -> dict[str, Any]:
        """Return mobile services."""
        url = f"{self.BASE_URL}/o/ecare/services"

        async with self._session.get(
            url,
            params={"serviceType": "Mobile"},
            headers=self._headers,
        ) as response:
            if response.status in (204, 401, 403):
                raise OneApiAuthenticationError(
                    f"One Hungary session rejected with status {response.status}"
                )

            response.raise_for_status()
            return await response.json(content_type=None)

    async def get_usage(self, msisdn: str) -> dict[str, Any]:
        """Return usage information for a mobile subscription."""
        url = f"{self.BASE_URL}/o/ecare/usages/ocs-usages"

        async with self._session.get(
            url,
            params={"msisdn": msisdn},
            headers=self._headers,
        ) as response:
            if response.status in (204, 401, 403):
                raise OneApiAuthenticationError(
                    f"One Hungary session rejected with status {response.status}"
                )

            response.raise_for_status()
            return await response.json(content_type=None)
