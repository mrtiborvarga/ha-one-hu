"""Buttons for One Hungary."""

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Set up buttons."""

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OneRefreshButton(coordinator),
        ]
    )


class OneRefreshButton(
    CoordinatorEntity,
    ButtonEntity,
):
    """Manual refresh button."""

    _attr_name = "One Hungary Refresh"
    _attr_unique_id = "one_hu_refresh"
    _attr_icon = "mdi:refresh"

    @property
    def device_info(self):
        """Attach button to One Hungary device."""
        return {
            "identifiers": {(DOMAIN, "one_hu")},
            "name": "One Hungary",
            "manufacturer": "One Hungary",
        }


    async def async_press(self) -> None:
        """Refresh data."""
        await self.coordinator.async_request_refresh()