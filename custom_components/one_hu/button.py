"""Buttons for One Hungary Unofficial."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .account_device import account_device_info
from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Set up One Hungary buttons."""
    coordinator: OneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OneRefreshButton(coordinator)])


class OneRefreshButton(
    CoordinatorEntity[OneDataUpdateCoordinator],
    ButtonEntity,
):
    """Manual refresh button."""

    _attr_has_entity_name = True
    _attr_name = "Refresh"
    _attr_unique_id = "one_hu_refresh"
    _attr_icon = "mdi:refresh"

    @property
    def device_info(self) -> DeviceInfo:
        """Attach the button to the account-level device."""
        return account_device_info(self.coordinator)

    async def async_press(self) -> None:
        """Request an immediate coordinator refresh."""
        await self.coordinator.async_request_refresh()
