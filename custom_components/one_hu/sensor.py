"""Sensors for One Hungary."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors."""

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OneMobileServicesCountSensor(coordinator),
        ]
    )


class OneMobileServicesCountSensor(CoordinatorEntity, SensorEntity):
    """Number of mobile services."""

    _attr_name = "One Hungary Mobile Services Count"
    _attr_unique_id = "one_hu_mobile_services_count"

    @property
    def native_value(self):
        """Return state."""
        return self.coordinator.data.get(
            "mobile_services_count",
            0,
        )
