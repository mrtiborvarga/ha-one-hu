"""Binary sensors for One Hungary."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator

EXTRA_SERVICE_DESCRIPTIONS = (
    ("331078", "Hívástartás"),
    ("331089", "Roaming üdvözlő SMS"),
    ("331079", "Hívószámkijelzés tiltás"),
    ("331085", "Mobil MMS szolgáltatás"),
    ("331074", "Hívásátirányítás (foglalt)"),
    ("331075", "Hívásátirányítás (feltétel nélküli)"),
    ("331076", "Hívásátirányítás"),
    ("331077", "Hívás várakoztatás"),
    ("331082", "Mobilvásárlás szolgáltatás"),
    ("331072", "Hívásátirányítás (nem elérhető)"),
    ("329570", "Hatósági felnőtt tartalom szűrés"),
    ("331084", "Hívásértesítő szolgáltatás"),
    ("331073", "Hívásátirányítás (nem válaszol)"),
    ("331090", "Roaming szolgáltatás"),
    ("331080", "Hívószámkijelzés"),
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
                service_name,
            )
            for service_id, service_name in EXTRA_SERVICE_DESCRIPTIONS
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

    _attr_name = "Prepaid"

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

    _attr_name = "eSIM"

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

    _attr_name = "Barred"

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
        service_name: str,
    ) -> None:
        """Initialize the extra service binary sensor."""
        super().__init__(coordinator, msisdn)

        self._service_id = service_id
        self._attr_name = service_name
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