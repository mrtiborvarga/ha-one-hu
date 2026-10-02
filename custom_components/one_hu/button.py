"""Button platform for One Hungary."""

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up button entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [OneHuRefreshButton(coordinator)],
    )


class OneHuRefreshButton(CoordinatorEntity, ButtonEntity):
    """Refresh One Hungary data."""

    _attr_name = "Refresh data"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "one_hu_refresh"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_request_refresh()