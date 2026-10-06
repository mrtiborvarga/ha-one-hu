"""API client for One Hungary Unofficial."""

from __future__ import annotations

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
        """Extract the CSRF token from the Cookie header.

        A request ``Cookie:`` header is just ``name=value`` pairs separated
        by ``;``, where the value may itself legally contain ``=``/``&``
        (e.g. OneTrust's ``OptanonConsent=isGpcEnabled=0&datestamp=...``).
        ``http.cookies.SimpleCookie`` targets the stricter ``Set-Cookie``
        value grammar and desyncs on such values, silently dropping every
        cookie that follows - including ``CSRF_TOKEN`` if it comes later in
        the header. Parse it manually instead.
        """
        for part in cookie_header.split(";"):
            name, _, value = part.strip().partition("=")

            if name == "CSRF_TOKEN":
                return value

        raise OneApiAuthenticationError(
            "CSRF_TOKEN was not found in the Cookie header"
        )

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

    async def _get_usage_endpoint(
        self,
        endpoint: str,
        msisdn: str,
    ) -> dict[str, Any]:
        """Return usage information from a specific usages endpoint."""
        url = f"{self.BASE_URL}/o/ecare/usages/{endpoint}"
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

    async def get_usage(self, msisdn: str) -> dict[str, Any]:
        """Return prepaid (OCS) usage information for a mobile subscription."""
        return await self._get_usage_endpoint("ocs-usages", msisdn)

    async def get_spr_usage(self, msisdn: str) -> dict[str, Any]:
        """Return postpaid data-allowance usage for a mobile subscription."""
        return await self._get_usage_endpoint("spr-usages", msisdn)

    async def get_rbm_usage(self, msisdn: str) -> dict[str, Any]:
        """Return postpaid voice-allowance usage for a mobile subscription."""
        return await self._get_usage_endpoint("rbm-usages", msisdn)
