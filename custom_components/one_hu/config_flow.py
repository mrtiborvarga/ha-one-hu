"""Config flow for One Hungary Unofficial."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries

from .api import OneApiAuthenticationError, OneApiClient
from .auth import CookieFileAuthProvider, CookieHeaderAuthProvider, OneAuthProvider
from .const import (
    AUTH_MODE_COOKIE_FILE,
    AUTH_MODE_COOKIE_HEADER,
    CONF_AUTH_MODE,
    CONF_COOKIE_FILE_PATH,
    CONF_COOKIE_HEADER,
    DOMAIN,
)


class OneHuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the authentication mode selection step."""

        if user_input is not None:
            if user_input[CONF_AUTH_MODE] == AUTH_MODE_COOKIE_FILE:
                return await self.async_step_cookie_file()
            return await self.async_step_cookie_header()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_AUTH_MODE, default=AUTH_MODE_COOKIE_HEADER
                    ): vol.In(
                        {
                            AUTH_MODE_COOKIE_HEADER: "Cookie Header",
                            AUTH_MODE_COOKIE_FILE: "Browser Profile (cookie export file)",
                        }
                    ),
                }
            ),
        )

    async def async_step_cookie_header(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the Cookie Header authentication mode."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cookie_header = user_input[CONF_COOKIE_HEADER]
            provider = CookieHeaderAuthProvider(cookie_header)
            errors = await self._async_validate_provider(provider)

            if not errors:
                return self.async_create_entry(
                    title="One Hungary",
                    data={
                        CONF_AUTH_MODE: AUTH_MODE_COOKIE_HEADER,
                        CONF_COOKIE_HEADER: cookie_header,
                    },
                )

        return self.async_show_form(
            step_id="cookie_header",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COOKIE_HEADER): str,
                }
            ),
            errors=errors,
        )

    async def async_step_cookie_file(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the Browser Profile (cookie export file) authentication mode."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cookie_file_path = user_input[CONF_COOKIE_FILE_PATH]
            provider = CookieFileAuthProvider(self.hass, cookie_file_path)
            errors = await self._async_validate_provider(provider)

            if not errors:
                return self.async_create_entry(
                    title="One Hungary",
                    data={
                        CONF_AUTH_MODE: AUTH_MODE_COOKIE_FILE,
                        CONF_COOKIE_FILE_PATH: cookie_file_path,
                    },
                )

        return self.async_show_form(
            step_id="cookie_file",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COOKIE_FILE_PATH): str,
                }
            ),
            errors=errors,
        )

    async def _async_validate_provider(
        self, provider: OneAuthProvider
    ) -> dict[str, str]:
        """Validate a candidate auth provider against the loginInfo endpoint."""
        # One Hungary responses carry very large headers (e.g. a sizeable
        # Content-Security-Policy), which exceed aiohttp's default 8190-byte
        # header limit and surface as a generic connection error. The
        # coordinator's session in __init__.py already raises these limits;
        # match that here with a short-lived session scoped to validation.
        async with aiohttp.ClientSession(
            max_line_size=65536, max_field_size=65536
        ) as session:
            api = OneApiClient(session=session, auth_provider=provider)

            try:
                await api.async_validate_session()
            except OneApiAuthenticationError:
                return {"base": "invalid_auth"}
            except aiohttp.ClientError:
                return {"base": "cannot_connect"}
            except Exception:  # noqa: BLE001
                return {"base": "unknown"}

        return {}
