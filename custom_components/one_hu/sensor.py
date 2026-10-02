"""Sensors for Unofficial One Hungary."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Set up One Hungary sensors."""

    coordinator: OneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        OneMobileServicesCountSensor(coordinator),
    ]

    for msisdn in coordinator.data.get("usage_by_msisdn", {}):
        entities.extend(
            [
                OneBalanceSensor(coordinator, msisdn),
                OneDaysAvailableSensor(coordinator, msisdn),
                OneBundlesCountSensor(coordinator, msisdn),
                OneBucketsCountSensor(coordinator, msisdn),
            ]
        )

    async_add_entities(entities)


class OneBaseSensor(
    CoordinatorEntity[OneDataUpdateCoordinator],
    SensorEntity,
):
    """Base sensor for a One Hungary mobile subscription."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._msisdn = msisdn

    @property
    def usage(self) -> dict[str, Any]:
        """Return usage information for this subscription."""
        return self.coordinator.data.get(
            "usage_by_msisdn",
            {},
        ).get(
            self._msisdn,
            {},
        )

    @property
    def available(self) -> bool:
        """Return whether usage data is available."""
        return (
            super().available
            and not self.usage.get("retrieveFailed", False)
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._msisdn)},
            name=f"One Hungary {self._msisdn}",
            manufacturer="One Hungary",
            model="Mobile subscription",
        )


class OneMobileServicesCountSensor(
    CoordinatorEntity[OneDataUpdateCoordinator],
    SensorEntity,
):
    """Number of mobile subscriptions."""

    _attr_has_entity_name = True
    _attr_name = "Mobile services count"
    _attr_unique_id = "one_hu_mobile_services_count"
    _attr_icon = "mdi:sim"

    @property
    def native_value(self) -> int:
        """Return the number of mobile subscriptions."""
        return self.coordinator.data.get(
            "mobile_services_count",
            0,
        )


class OneBalanceSensor(OneBaseSensor):
    """Balance of a mobile subscription."""

    entity_description = SensorEntityDescription(
        key="balance",
        name="Balance",
        icon="mdi:cash",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the balance sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_balance"

    @property
    def native_value(self) -> float | None:
        """Return the balance."""
        value = self.usage.get("balance")

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class OneDaysAvailableSensor(OneBaseSensor):
    """Available days for a mobile subscription."""

    entity_description = SensorEntityDescription(
        key="days_available",
        name="Days available",
        icon="mdi:calendar-clock",
        native_unit_of_measurement="d",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the days available sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_days_available"

    @property
    def native_value(self) -> int | None:
        """Return available days."""
        value = self.usage.get("daysAvailable")

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class OneBundlesCountSensor(OneBaseSensor):
    """Number of bundles for a mobile subscription."""

    entity_description = SensorEntityDescription(
        key="bundles_count",
        name="Bundles count",
        icon="mdi:package-variant",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the bundles sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_bundles_count"

    @property
    def native_value(self) -> int:
        """Return the number of bundles."""
        bundles = self.usage.get("bundles", [])
        return len(bundles) if isinstance(bundles, list) else 0


class OneBucketsCountSensor(OneBaseSensor):
    """Number of buckets for a mobile subscription."""

    entity_description = SensorEntityDescription(
        key="buckets_count",
        name="Buckets count",
        icon="mdi:format-list-bulleted",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the buckets sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_buckets_count"

    @property
    def native_value(self) -> int:
        """Return the number of buckets."""
        buckets = self.usage.get("buckets", [])
        return len(buckets) if isinstance(buckets, list) else 0

from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
