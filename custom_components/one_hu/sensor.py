"""Sensors for One Hungary Unofficial."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .account_device import (
    account_device_info,
    account_identifier,
    account_key,
)
from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Set up One Hungary sensors."""
    coordinator: OneDataUpdateCoordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    entities: list[SensorEntity] = [
        OneMobileServicesCountSensor(coordinator),
        OneLastSuccessfulSyncSensor(coordinator),
        OneApiStatusSensor(coordinator),
    ]

    for msisdn in coordinator.data.get(
        "usage_by_msisdn",
        {},
    ):
        entities.extend(
            [
                OneBalanceSensor(coordinator, msisdn),
                OneDaysAvailableSensor(
                    coordinator,
                    msisdn,
                ),
                OneBundlesCountSensor(
                    coordinator,
                    msisdn,
                ),
                OneBucketsCountSensor(
                    coordinator,
                    msisdn,
                ),
                OneDataAllowanceSensor(
                    coordinator,
                    msisdn,
                ),
                OneDataRemainingSensor(
                    coordinator,
                    msisdn,
                ),
                OneDataUsedSensor(
                    coordinator,
                    msisdn,
                ),
                OneDataUsedPercentageSensor(
                    coordinator,
                    msisdn,
                ),
                OneDataExpiresInSensor(
                    coordinator,
                    msisdn,
                ),
                OneTariffNameSensor(
                    coordinator,
                    msisdn,
                ),
                OneSubscriptionStatusSensor(
                    coordinator,
                    msisdn,
                ),
                One100MBRemainingSensor(
                    coordinator,
                    msisdn,
                ),
                One100MBExpiresInSensor(
                    coordinator,
                    msisdn,
                ),
            ]
        )

    async_add_entities(entities)


class OneAccountSensor(
    CoordinatorEntity[OneDataUpdateCoordinator],
    SensorEntity,
):
    """Base sensor for the One Hungary account device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        key: str,
    ) -> None:
        """Initialize an account-level sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{account_key(coordinator)}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return account-level device information."""
        return account_device_info(self.coordinator)


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
        """Initialize the subscription sensor."""
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
            and not self.usage.get(
                "retrieveFailed",
                False,
            )
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return subscription device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._msisdn)},
            name=f"One Hungary {self._msisdn}",
            manufacturer="One Hungary",
            model="Mobile subscription",
            via_device=account_identifier(self.coordinator),
        )


class OneMobileServicesCountSensor(OneAccountSensor):
    """Number of mobile subscriptions."""

    _attr_name = "Mobile services count"
    _attr_icon = "mdi:sim"

    def __init__(self, coordinator: OneDataUpdateCoordinator) -> None:
        """Initialize the account mobile-services sensor."""
        super().__init__(coordinator, "mobile_services_count")

    @property
    def native_value(self) -> int:
        """Return the number of mobile subscriptions."""
        return self.coordinator.data.get(
            "mobile_services_count",
            0,
        )


class OneLastSuccessfulSyncSensor(OneAccountSensor):
    """Last successful synchronization."""

    _attr_name = "Last successful sync"
    _attr_icon = "mdi:clock-check"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: OneDataUpdateCoordinator) -> None:
        """Initialize the last-successful-sync sensor."""
        super().__init__(coordinator, "last_successful_sync")

    @property
    def native_value(self):
        """Return the last successful synchronization."""
        return self.coordinator.data.get(
            "last_successful_sync"
        )


class OneApiStatusSensor(OneAccountSensor):
    """One Hungary API status."""

    _attr_name = "API status"
    _attr_icon = "mdi:lan-connect"

    def __init__(self, coordinator: OneDataUpdateCoordinator) -> None:
        """Initialize the account API-status sensor."""
        super().__init__(coordinator, "api_status")

    @property
    def native_value(self) -> str:
        """Return the API status."""
        return self.coordinator.data.get(
            "api_status",
            "Unknown",
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
        """Initialize the available-days sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_days_available"
        )

    @property
    def native_value(self) -> int | None:
        """Return the available days."""
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
        """Initialize the bundles-count sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_bundles_count"
        )

    @property
    def extra_state_attributes(
        self,
    ) -> dict[str, Any]:
        """Return parsed allowance information."""
        return {
            "allowances": self.usage.get(
                "allowances",
                [],
            )
        }

    @property
    def native_value(self) -> int:
        """Return the number of bundles."""
        bundles = self.usage.get("bundles", [])

        return (
            len(bundles)
            if isinstance(bundles, list)
            else 0
        )


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
        """Initialize the buckets-count sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_buckets_count"
        )

    @property
    def native_value(self) -> int:
        """Return the number of buckets."""
        buckets = self.usage.get("buckets", [])

        return (
            len(buckets)
            if isinstance(buckets, list)
            else 0
        )


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
        """Initialize the data-allowance sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_data_allowance"
        )

    @property
    def native_value(self) -> float | None:
        """Return the total data allowance in GB."""
        return (
            self.usage
            .get("data_summary", {})
            .get("total_gb")
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
        """Initialize the remaining-data sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_data_remaining"
        )

    @property
    def native_value(self) -> float | None:
        """Return remaining data in GB."""
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
        """Initialize the used-data sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_data_used"

    @property
    def native_value(self) -> float | None:
        """Return used data in GB."""
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
        """Initialize the percentage sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_data_used_percentage"
        )

    @property
    def native_value(self) -> float | None:
        """Return the used-data percentage."""
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
        """Initialize the data-expiration sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_data_expires_in"
        )

    @property
    def native_value(self) -> int | None:
        """Return the remaining days."""
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
        """Initialize the tariff sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_tariff"

    @property
    def native_value(self) -> str | None:
        """Return the tariff name."""
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
        """Initialize the subscription-status sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_subscription_status"
        )

    @property
    def native_value(self) -> str | None:
        """Return the subscription status."""
        status = self.service.get("status", {})

        if not isinstance(status, dict):
            return None

        return status.get("name")


class One100MBRemainingSensor(OneBaseSensor):
    """Remaining volume of the 100MB data allowance."""

    entity_description = SensorEntityDescription(
        key="100mb_adat_remaining",
        name="100MB adat Remaining",
        icon="mdi:database",
        native_unit_of_measurement="MB",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the 100MB remaining sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_100mb_adat_remaining"
        )

    @property
    def native_value(self) -> float | None:
        """Return the remaining 100MB allowance."""
        allowance = (
            self.usage
            .get("allowance_summary", {})
            .get("100MB adat")
        )

        if not isinstance(allowance, dict):
            return None

        value = allowance.get("remaining")

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class One100MBExpiresInSensor(OneBaseSensor):
    """Expiration of the 100MB data allowance."""

    entity_description = SensorEntityDescription(
        key="100mb_adat_expires_in",
        name="100MB adat Expires In",
        icon="mdi:calendar-clock",
        native_unit_of_measurement="d",
    )

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        """Initialize the 100MB expiration sensor."""
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = (
            f"{msisdn}_100mb_adat_expires_in"
        )

    @property
    def native_value(self) -> int | None:
        """Return expiration in days."""
        allowance = (
            self.usage
            .get("allowance_summary", {})
            .get("100MB adat")
        )

        if not isinstance(allowance, dict):
            return None

        value = allowance.get("days_to_expire")

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None