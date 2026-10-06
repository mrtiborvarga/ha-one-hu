"""Binary sensors for One Hungary."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator

EXTRA_SERVICE_DESCRIPTIONS = (
    ("331078", "call_hold"),
    ("331089", "roaming_welcome_sms"),
    ("331079", "caller_id_restriction"),
    ("331085", "mobile_mms_service"),
    ("331074", "call_forwarding_busy"),
    ("331075", "call_forwarding_unconditional"),
    ("331076", "call_forwarding"),
    ("331077", "call_waiting"),
    ("331082", "mobile_purchase_service"),
    ("331072", "call_forwarding_unreachable"),
    ("329570", "adult_content_filter"),
    ("331084", "call_notification_service"),
    ("331073", "call_forwarding_no_answer"),
    ("331090", "roaming_service"),
    ("331080", "caller_id"),
)

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Set up One Hungary binary sensors."""

    coordinator: OneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for msisdn in coordinator.data.get("service_by_msisdn", {}):
        entities.extend(
            [
                OnePrepaidBinarySensor(coordinator, msisdn),
                OneESimBinarySensor(coordinator, msisdn),
                OneBarredBinarySensor(coordinator, msisdn),
            ]
        )
        entities.extend(
            OneExtraServiceBinarySensor(
                coordinator,
                msisdn,
                service_id,
                translation_key,
            )
            for service_id, translation_key in EXTRA_SERVICE_DESCRIPTIONS
        )
    async_add_entities(entities)


class OneBaseBinarySensor(
    CoordinatorEntity[OneDataUpdateCoordinator],
    BinarySensorEntity,
):
    """Base binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator)
        self._msisdn = msisdn

    @property
    def service(self) -> dict:
        """Return service information."""
        return self.coordinator.data.get(
            "service_by_msisdn",
            {},
        ).get(
            self._msisdn,
            {},
        )

    @property
    def device_info(self):
        """Device information."""
        return {
            "identifiers": {(DOMAIN, self._msisdn)},
        }


class OnePrepaidBinarySensor(OneBaseBinarySensor):
    """Prepaid status."""

    _attr_translation_key = "prepaid"

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_prepaid"

    @property
    def is_on(self) -> bool:
        return bool(self.service.get("prepaidLine"))


class OneESimBinarySensor(OneBaseBinarySensor):
    """eSIM status."""

    _attr_translation_key = "esim"

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_esim"

    @property
    def is_on(self) -> bool:
        return bool(self.service.get("eSim"))


class OneBarredBinarySensor(OneBaseBinarySensor):
    """Barred status."""

    _attr_translation_key = "barred"

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
    ) -> None:
        super().__init__(coordinator, msisdn)
        self._attr_unique_id = f"{msisdn}_barred"

    @property
    def is_on(self) -> bool:
        return bool(self.service.get("barred"))

class OneExtraServiceBinarySensor(OneBaseBinarySensor):
    """Active state of a One Hungary extra service."""

    _attr_icon = "mdi:toggle-switch"
    _attr_entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator: OneDataUpdateCoordinator,
        msisdn: str,
        service_id: str,
        translation_key: str,
    ) -> None:
        """Initialize the extra service binary sensor."""
        super().__init__(coordinator, msisdn)

        self._service_id = service_id
        self._attr_translation_key = translation_key
        self._attr_unique_id = (
            f"{msisdn}_extra_service_{service_id}"
        )

    @property
    def extra_service(self) -> dict:
        """Return extra service information."""
        return (
            self.service
            .get("extraServices", {})
            .get("entities", {})
            .get(self._service_id, {})
        )

    @property
    def available(self) -> bool:
        """Return whether the extra service is reported by One."""
        return (
            super().available
            and bool(self.extra_service)
        )

    @property
    def is_on(self) -> bool:
        """Return whether the extra service is active."""
        return bool(self.extra_service.get("active", False))