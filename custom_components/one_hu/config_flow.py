"""Config flow for Unofficial One Hungary."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_COOKIE_HEADER,
    DOMAIN,
)

class OneHuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        if user_input is not None:
            return self.async_create_entry(
                title="One Hungary",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                   vol.Required(CONF_COOKIE_HEADER): str,
                }
            ),
        )