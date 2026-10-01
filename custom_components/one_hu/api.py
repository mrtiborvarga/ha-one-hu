"""API client for Unofficial One Hungary."""

from __future__ import annotations


class OneApiClient:
    """One Hungary API client."""

    def __init__(self, session_cookie: str, csrf_token: str) -> None:
        self._session_cookie = session_cookie
        self._csrf_token = csrf_token

    async def get_services(self):
        """Return mobile services."""
        raise NotImplementedError

    async def get_usage(self, msisdn: str):
        """Return usage data for a phone number."""
        raise NotImplementedError
