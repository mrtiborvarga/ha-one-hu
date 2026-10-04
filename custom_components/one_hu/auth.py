"""Authentication providers for One Hungary Unofficial.

An OneAuthProvider resolves the Cookie header that OneApiClient attaches to
every request. CookieHeaderAuthProvider wraps a header pasted by the user
directly into the config entry. CookieFileAuthProvider reads a cookie header
from a JSON file that is refreshed by the external tools/one_login.py helper,
which performs the actual browser-based login with Playwright. Home Assistant
itself never launches a browser.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from .api import OneApiAuthenticationError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class OneAuthProvider:
    """Base class for One Hungary authentication providers."""

    async def async_get_cookie_header(self) -> str:
        """Return the current Cookie header to use for API requests."""
        raise NotImplementedError


class CookieHeaderAuthProvider(OneAuthProvider):
    """Provide a Cookie header configured directly by the user."""

    def __init__(self, cookie_header: str) -> None:
        """Initialize the provider."""
        self._cookie_header = cookie_header

    async def async_get_cookie_header(self) -> str:
        """Return the configured Cookie header."""
        return self._cookie_header


class CookieFileAuthProvider(OneAuthProvider):
    """Provide a Cookie header read from a file exported by tools/one_login.py."""

    def __init__(self, hass: HomeAssistant, cookie_file_path: str) -> None:
        """Initialize the provider."""
        self._hass = hass
        self._path = Path(cookie_file_path)

    async def async_get_cookie_header(self) -> str:
        """Return the Cookie header currently stored in the cookie file."""
        return await self._hass.async_add_executor_job(self._read_cookie_header)

    def _read_cookie_header(self) -> str:
        """Read and parse the cookie file. Runs in an executor thread."""
        if not self._path.is_file():
            raise OneApiAuthenticationError(
                f"Cookie file not found at {self._path}. "
                "Run tools/one_login.py to create it."
            )

        try:
            raw_content = self._path.read_text(encoding="utf-8")
            data = json.loads(raw_content)
        except (OSError, ValueError) as err:
            raise OneApiAuthenticationError(
                f"Unable to read cookie file at {self._path}: {err}"
            ) from err

        cookie_header = data.get("cookie_header")

        if not cookie_header:
            raise OneApiAuthenticationError(
                f"Cookie file at {self._path} does not contain a cookie_header. "
                "Run tools/one_login.py to refresh it."
            )

        return cookie_header
