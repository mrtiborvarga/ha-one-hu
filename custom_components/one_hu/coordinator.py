"""Data coordinator for Unofficial One Hungary."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import OneApiAuthenticationError, OneApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


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
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch subscriptions and usage information."""
        try:
            services_response = await self.api.get_services()
        except OneApiAuthenticationError as err:
            raise UpdateFailed(
                "The One Hungary browser session is invalid or expired"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Unable to retrieve subscriptions from One Hungary: {err}"
            ) from err

        services = services_response.get("services", {})
        menu_items = services.get("menuItems", [])
        entities = services.get("entities", {})

        usage_by_msisdn: dict[str, dict[str, Any]] = {}

        for menu_item in menu_items:
            service_id = str(menu_item.get("id", ""))
            service = entities.get(service_id, {})

            msisdn = str(
                service.get("msisdn")
                or menu_item.get("title")
                or ""
            )

            if not msisdn:
                continue

            try:
                usage = await self.api.get_usage(msisdn)
            except OneApiAuthenticationError as err:
                raise UpdateFailed(
                    "The One Hungary browser session is invalid or expired"
                ) from err
            except Exception as err:
                _LOGGER.warning(
                    "Unable to retrieve usage for %s: %s",
                    msisdn,
                    err,
                )
                usage = {
                    "retrieveFailed": True,
                    "error": str(err),
                    "balance": None,
                    "daysAvailable": None,
                    "bundles": [],
                    "buckets": [],
                }

            usage_by_msisdn[msisdn] = usage

        return {
            "services_response": services_response,
            "mobile_services_count": len(menu_items),
            "services": entities,
            "usage_by_msisdn": usage_by_msisdn,
        }