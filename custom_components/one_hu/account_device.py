"""Account-level device helpers for One Hungary Unofficial."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import OneDataUpdateCoordinator


def account_identifier(
    coordinator: OneDataUpdateCoordinator,
) -> tuple[str, str]:
    """Return the unique account device identifier."""
    primary_account = coordinator.data.get(
        "primary_account",
        {},
    )

    account_id = str(
        primary_account.get("id")
        or primary_account.get("individualId")
        or "unknown"
    )

    return DOMAIN, f"account_{account_id}"

def account_key(
    coordinator: OneDataUpdateCoordinator,
) -> str:
    """Return a stable account key for entity unique IDs."""
    return account_identifier(coordinator)[1]

def account_device_name(
    coordinator: OneDataUpdateCoordinator,
) -> str:
    """Return the account-level device name."""
    primary_account = coordinator.data.get(
        "primary_account",
        {},
    )

    account_title = primary_account.get("title")

    if account_title:
        return f"One Hungary ({account_title})"

    return "One Hungary"


def account_device_info(
    coordinator: OneDataUpdateCoordinator,
) -> DeviceInfo:
    """Return account-level device information."""
    return DeviceInfo(
        identifiers={account_identifier(coordinator)},
        name=account_device_name(coordinator),
        manufacturer="One Hungary",
        model="One Hungary account",
        configuration_url="https://www.one.hu",
    )


def subscription_device_info(
    coordinator: OneDataUpdateCoordinator,
    msisdn: str,
) -> DeviceInfo:
    """Return device information for a mobile subscription."""
    return DeviceInfo(
        identifiers={(DOMAIN, msisdn)},
        name=f"One Hungary {msisdn}",
        manufacturer="One Hungary",
        model="Mobile subscription",
        via_device=account_identifier(coordinator),
    )
