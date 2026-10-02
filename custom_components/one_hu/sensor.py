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
        OneLastSuccessfulSyncSensor(coordinator),
        OneApiStatusSensor(coordinator),
      ]

    for msisdn in coordinator.data.get("usage_by_msisdn", {}):
        entities.extend(
            [
                OneBalanceSensor(coordinator, msisdn),
                OneDaysAvailableSensor(coordinator, msisdn),
                OneBundlesCountSensor(coordinator, msisdn),
                OneBucketsCountSensor(coordinator, msisdn),

                OneDataAllowanceSensor(coordinator, msisdn),
                OneDataRemainingSensor(coordinator, msisdn),
                OneDataUsedSensor(coordinator, msisdn),
                OneDataUsedPercentageSensor(coordinator, msisdn),
                OneDataExpiresInSensor(coordinator, msisdn),
                OneTariffNameSensor(coordinator, msisdn),
                OneSubscriptionStatusSensor(coordinator, msisdn),
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
    def service(self) -> dict[str, Any]:
        """Return service information for this subscription."""
        return self.coordinator.data.get(
            "service_by_msisdn",
            {},
        ).get(
            self._msisdn,
            {},
        )

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
    def device_info(self) -> DeviceInfo:
        """Return integration device."""
        return DeviceInfo(
            identifiers={(DOMAIN, "one_hu")},
            name="One Hungary",
            manufacturer="One Hungary",
            configuration_url="https://www.one.hu",
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return integration device."""
        return DeviceInfo(
            identifiers={(DOMAIN, "one_hu")},
            name="One Hungary",
            manufacturer="One Hungary",
        )

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

class OneDataAllowanceSensor(OneBaseSensor):
    """Total data allowance."""

    entity_description = SensorEntityDescription(
        key="data_allowance",
        name="Data allowance",
        icon="mdi:database",
        native_unit_of_measurement="GB",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_data_allowance"

    @property
    def native_value(self) -> float | None:
        """Return total allowance in GB."""
        return (
            self.usage
            .get("data_summary", {})
            .get("total_gb")
        )

class OneLastSuccessfulSyncSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Last successful sync."""

    _attr_name = "One Hungary Last Successful Sync"
    _attr_unique_id = "one_hu_last_successful_sync"
    _attr_icon = "mdi:clock-check"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def device_info(self) -> DeviceInfo:
        """Return integration device."""
        return DeviceInfo(
            identifiers={(DOMAIN, "one_hu")},
            name="One Hungary",
            manufacturer="One Hungary",
            configuration_url="https://www.one.hu",
        )

    @property
    def native_value(self):
        """Return timestamp."""
        return self.coordinator.data.get(
            "last_successful_sync"
        )

class OneApiStatusSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """One Hungary API status."""

    _attr_name = "One Hungary API Status"
    _attr_unique_id = "one_hu_api_status"
    _attr_icon = "mdi:lan-connect"

    @property
    def device_info(self) -> DeviceInfo:
        """Return integration device."""
        return DeviceInfo(
            identifiers={(DOMAIN, "one_hu")},
            name="One Hungary",
            manufacturer="One Hungary",
        )

    @property
    def native_value(self):
        """Return API status."""
        return self.coordinator.data.get(
            "api_status",
            "Unknown",
        )

class OneDataRemainingSensor(OneBaseSensor):
    """Remaining data."""

    entity_description = SensorEntityDescription(
        key="data_remaining",
        name="Data remaining",
        icon="mdi:database-check",
        native_unit_of_measurement="GB",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_data_remaining"

    @property
    def native_value(self) -> float | None:
        return (
            self.usage
            .get("data_summary", {})
            .get("remaining_gb")
        )

class OneDataUsedSensor(OneBaseSensor):
    """Used data."""

    entity_description = SensorEntityDescription(
        key="data_used",
        name="Data used",
        icon="mdi:database-minus",
        native_unit_of_measurement="GB",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_data_used"

    @property
    def native_value(self) -> float | None:
        return (
            self.usage
            .get("data_summary", {})
            .get("used_gb")
        )

class OneDataUsedPercentageSensor(OneBaseSensor):
    """Used data percentage."""

    entity_description = SensorEntityDescription(
        key="data_used_percentage",
        name="Data used percentage",
        icon="mdi:percent",
        native_unit_of_measurement="%",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_data_used_percentage"

    @property
    def native_value(self) -> float | None:
        return (
            self.usage
            .get("data_summary", {})
            .get("used_percentage")
        )

class OneDataExpiresInSensor(OneBaseSensor):
    """Data expiration in days."""

    entity_description = SensorEntityDescription(
        key="data_expires_in",
        name="Data expires in",
        icon="mdi:calendar-end",
        native_unit_of_measurement="d",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_data_expires_in"

    @property
    def native_value(self) -> int | None:
        return (
            self.usage
            .get("data_summary", {})
            .get("days_to_expire")
        )

class OneTariffNameSensor(OneBaseSensor):
    """Tariff name."""

    entity_description = SensorEntityDescription(
        key="tariff_name",
        name="Tariff",
        icon="mdi:ticket-account",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_tariff"

    @property
    def native_value(self) -> str | None:
        return self.service.get("tariffName")

class OneSubscriptionStatusSensor(OneBaseSensor):
    """Subscription status."""

    entity_description = SensorEntityDescription(
        key="subscription_status",
        name="Subscription status",
        icon="mdi:sim",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_subscription_status"

    @property
    def native_value(self) -> str | None:
        status = self.service.get("status", {})
        return status.get("name")
