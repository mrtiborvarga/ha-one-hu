"""One Hungary Unofficial integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import OneApiClient
from .auth import CookieFileAuthProvider, CookieHeaderAuthProvider
from .const import (
    AUTH_MODE_COOKIE_FILE,
    AUTH_MODE_COOKIE_HEADER,
    CONF_AUTH_MODE,
    CONF_COOKIE_FILE_PATH,
    CONF_COOKIE_HEADER,
    DOMAIN,
)
from .coordinator import OneDataUpdateCoordinator

PLATFORMS = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up One Hungary from a config entry."""

    session = async_create_clientsession(
    hass,
    max_line_size=65536,
    max_field_size=65536,
    )

    auth_mode = entry.data.get(CONF_AUTH_MODE, AUTH_MODE_COOKIE_HEADER)

    if auth_mode == AUTH_MODE_COOKIE_FILE:
        auth_provider = CookieFileAuthProvider(
            hass=hass,
            cookie_file_path=entry.data[CONF_COOKIE_FILE_PATH],
        )
    else:
        auth_provider = CookieHeaderAuthProvider(
            cookie_header=entry.data[CONF_COOKIE_HEADER],
        )

    api = OneApiClient(
        session=session,
        auth_provider=auth_provider,
    )

    coordinator = OneDataUpdateCoordinator(
        hass=hass,
        api=api,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a One Hungary config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok