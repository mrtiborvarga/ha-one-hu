"""Account-level device helpers for One Hungary Unofficial."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator


def account_device_name(
    coordinator: OneDataUpdateCoordinator,
) -> str:
    """Return the account-level device name."""
    primary_account = coordinator.data.get("primary_account", {})
    account_title = primary_account.get("title")

    if account_title:
        return f"One Hungary ({account_title})"

    return "One Hungary"


def account_device_info(
    coordinator: OneDataUpdateCoordinator,
) -> DeviceInfo:
    """Return account-level device information."""
    return DeviceInfo(
        identifiers={(DOMAIN, "one_hu")},
        name=account_device_name(coordinator),
        manufacturer="One Hungary",
        model="One Hungary account",
        configuration_url="https://www.one.hu",
    )
