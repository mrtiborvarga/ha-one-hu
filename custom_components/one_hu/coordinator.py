"""Data coordinator for Unofficial One Hungary."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OneApiAuthenticationError, OneApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class OneDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate updates from the One Hungary API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: OneApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest mobile subscription data."""
        try:
            services = await self.api.get_services()
        except OneApiAuthenticationError as err:
            raise UpdateFailed(
                "The One Hungary browser session is invalid or expired"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Unable to retrieve data from One Hungary: {err}"
            ) from err

        menu_items = (
            services
            .get("services", {})
            .get("menuItems", [])
        )

        return {
            "services_response": services,
            "mobile_services_count": len(menu_items),
        }