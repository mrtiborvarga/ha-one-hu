"""API client for One Hungary Unofficial."""

from __future__ import annotations

from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from .auth import OneAuthProvider


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
        auth_provider: OneAuthProvider,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._auth_provider = auth_provider

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

    async def _async_headers(self) -> dict[str, str]:
        """Return API request headers for the current session."""
        cookie_header = await self._auth_provider.async_get_cookie_header()
        csrf_token = self._extract_csrf_token(cookie_header)

        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            "Cookie": cookie_header,
            "X-Csrf-Token": csrf_token,
        }

    async def async_validate_session(self) -> bool:
        """Validate the current session using the loginInfo endpoint."""
        url = f"{self.BASE_URL}/o/ecare/loginInfo"
        headers = await self._async_headers()

        async with self._session.get(url, headers=headers) as response:
            if response.status in (204, 401, 403):
                raise OneApiAuthenticationError(
                    f"One Hungary session rejected with status {response.status}"
                )

            response.raise_for_status()
            data = await response.json(content_type=None)

        if not (
            data.get("authorized")
            and data.get("active")
            and data.get("sessionInitialized")
        ):
            raise OneApiAuthenticationError(
                "One Hungary session is not authorized or not active"
            )

        return True

    async def get_services(self) -> dict[str, Any]:
        """Return mobile services."""
        url = f"{self.BASE_URL}/o/ecare/services"
        headers = await self._async_headers()

        async with self._session.get(
            url,
            params={"serviceType": "Mobile"},
            headers=headers,
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
        headers = await self._async_headers()

        async with self._session.get(
            url,
            params={"msisdn": msisdn},
            headers=headers,
        ) as response:
            if response.status in (204, 401, 403):
                raise OneApiAuthenticationError(
                    f"One Hungary session rejected with status {response.status}"
                )

            response.raise_for_status()
            return await response.json(content_type=None)
