"""Data coordinator for One Hungary Unofficial."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import OneApiAuthenticationError, OneApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

_BYTES_PER_MB = 1024**2
_BYTES_PER_GB = 1024**3


def _quantity_to_bytes(value: Any, unit: str) -> float:
    """Convert a data quantity to bytes."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    normalized_unit = unit.upper()

    if normalized_unit == "GB":
        return numeric_value * _BYTES_PER_GB

    if normalized_unit == "MB":
        return numeric_value * _BYTES_PER_MB

    if normalized_unit in {"B", "BYTE", "BYTES"}:
        return numeric_value

    return 0.0


def _summarize_data_buckets(
    usage: dict[str, Any],
) -> dict[str, float | int | None]:
    """Summarize data buckets in a common unit."""
    total_bytes = 0.0
    remaining_bytes = 0.0
    expiry_dates: list[int] = []
    days_to_expire: list[int] = []

    for bucket in usage.get("buckets", []):
        if not isinstance(bucket, dict):
            continue

        offer = bucket.get("offer", {})
        domains = bucket.get("domainSSP", [])

        domain_type = str(offer.get("domainType", ""))
        is_data_bucket = (
            "Data" in domain_type
            or any("Data" in str(domain) for domain in domains)
        )

        if not is_data_bucket:
            continue

        total_bucket_bytes = offer.get("numericVolume")

        try:
            total_bucket_bytes = float(total_bucket_bytes)
        except (TypeError, ValueError):
            total_bucket_bytes = 0.0

        if total_bucket_bytes <= 0:
            total_bucket_bytes = _quantity_to_bytes(
                offer.get("volume"),
                str(offer.get("units", "")),
            )

        remaining_bucket_bytes = _quantity_to_bytes(
            bucket.get("counter"),
            str(bucket.get("units") or offer.get("units", "")),
        )

        total_bytes += total_bucket_bytes
        remaining_bytes += remaining_bucket_bytes

        end_date = bucket.get("endDate")
        to_end = bucket.get("toEnd")

        if isinstance(to_end, int):
            days_to_expire.append(to_end)

        if isinstance(end_date, int):
            expiry_dates.append(end_date)

    used_bytes = max(total_bytes - remaining_bytes, 0.0)

    used_percentage = (
        round((used_bytes / total_bytes) * 100, 1)
        if total_bytes > 0
        else None
    )

    return {
        "total_gb": round(total_bytes / _BYTES_PER_GB, 3),
        "remaining_gb": round(remaining_bytes / _BYTES_PER_GB, 3),
        "used_gb": round(used_bytes / _BYTES_PER_GB, 3),
        "used_percentage": used_percentage,
        "expires_at": min(expiry_dates) if expiry_dates else None,
        "days_to_expire": min(days_to_expire) if days_to_expire else None,
    }


def _summarize_postpaid_data(
    allowances_by_category: dict[str, list[dict[str, Any]]],
) -> dict[str, float | int | None]:
    """Summarize postpaid (spr-usages) data allowances in a common unit."""
    total_bytes = 0.0
    remaining_bytes = 0.0
    days_to_expire: list[int] = []

    for category, items in allowances_by_category.items():
        for item in items:
            if not isinstance(item, dict):
                continue

            item_type = str(item.get("type") or category)

            if "Data" not in item_type:
                continue

            total_bytes += _quantity_to_bytes(
                item.get("initialVolume"),
                str(item.get("initialUnit", "")),
            )
            remaining_bytes += _quantity_to_bytes(
                item.get("leftVolume"),
                str(item.get("leftUnit", "")),
            )

            reset_days = item.get("daysBeforeReset")

            if isinstance(reset_days, int):
                days_to_expire.append(reset_days)

    used_bytes = max(total_bytes - remaining_bytes, 0.0)

    used_percentage = (
        round((used_bytes / total_bytes) * 100, 1)
        if total_bytes > 0
        else None
    )

    return {
        "total_gb": round(total_bytes / _BYTES_PER_GB, 3),
        "remaining_gb": round(remaining_bytes / _BYTES_PER_GB, 3),
        "used_gb": round(used_bytes / _BYTES_PER_GB, 3),
        "used_percentage": used_percentage,
        "expires_at": None,
        "days_to_expire": min(days_to_expire) if days_to_expire else None,
    }


class OneDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate updates from the One Hungary API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: OneApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch subscriptions and usage information."""
        try:
            services_response = await self.api.get_services()
        except OneApiAuthenticationError as err:
            raise UpdateFailed(
                "The One Hungary browser session is invalid or expired"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Unable to retrieve subscriptions from One Hungary: {err}"
            ) from err

        services = services_response.get("services", {})
        accounts = services_response.get("accounts", [])
        menu_items = services.get("menuItems", [])
        entities = services.get("entities", {})

        service_by_msisdn: dict[str, dict[str, Any]] = {}
        usage_by_msisdn: dict[str, dict[str, Any]] = {}

        for menu_item in menu_items:
            service_id = str(menu_item.get("id", ""))
            service = entities.get(service_id, {})

            msisdn = str(
                service.get("msisdn")
                or menu_item.get("title")
                or ""
            )

            if not msisdn:
                continue
            service_by_msisdn[msisdn] = service

            try:
                usage = await self.api.get_usage(msisdn)
            except OneApiAuthenticationError as err:
                raise UpdateFailed(
                    "The One Hungary browser session is invalid or expired"
                ) from err
            except Exception as err:
                _LOGGER.warning(
                    "Unable to retrieve usage for %s: %s",
                    msisdn,
                    err,
                )
                usage = {
                    "retrieveFailed": True,
                    "error": str(err),
                    "balance": None,
                    "daysAvailable": None,
                    "bundles": [],
                    "buckets": [],
                }

            postpaid_allowances: dict[str, list[dict[str, Any]]] = {}

            if usage.get("retrieveFailed"):
                # Postpaid ("havidíjas") lines aren't served by
                # ocs-usages; fall back to the postpaid data/voice
                # usage endpoints instead.
                for endpoint_getter in (
                    self.api.get_spr_usage,
                    self.api.get_rbm_usage,
                ):
                    try:
                        postpaid_usage = await endpoint_getter(msisdn)
                    except Exception as err:  # noqa: BLE001
                        _LOGGER.debug(
                            "Postpaid usage fallback failed for %s via %s: %s",
                            msisdn,
                            endpoint_getter.__name__,
                            err,
                        )
                        continue

                    if not isinstance(postpaid_usage, dict):
                        continue

                    if postpaid_usage.get("retrieveFailed"):
                        continue

                    postpaid_allowances.update(
                        postpaid_usage.get("allowances", {}) or {}
                    )

                if postpaid_allowances:
                    usage = {
                        "retrieveFailed": False,
                        "balance": None,
                        "daysAvailable": None,
                        "bundles": [],
                        "buckets": [],
                    }

            usage["data_summary"] = (
                _summarize_postpaid_data(postpaid_allowances)
                if postpaid_allowances
                else _summarize_data_buckets(usage)
            )

            usage["allowances"] = []
            usage["allowance_summary"] = {}

            if postpaid_allowances:
                for items in postpaid_allowances.values():
                    for allowance in items:
                        allowance_name = allowance.get("name")

                        allowance_data = {
                            "name": allowance_name,
                            "remaining": (
                                allowance.get("leftVolume")
                                if allowance.get("leftVolume")
                                is not None
                                else allowance.get(
                                    "remainingAllowance"
                                )
                            ),
                            "units": (
                                allowance.get("leftUnit")
                                or allowance.get("unit")
                            ),
                            "days_to_expire": allowance.get(
                                "daysBeforeReset"
                            ),
                            "type": allowance.get("type"),
                        }

                        usage["allowances"].append(allowance_data)

                        if allowance_name:
                            usage["allowance_summary"][
                                allowance_name
                            ] = allowance_data
            else:
                for bundle in usage.get("bundles", []):
                    for allowance in bundle.get("allowances", []):

                        allowance_name = (
                            allowance
                            .get("offer", {})
                            .get("name")
                        )

                        allowance_data = {
                            "name": allowance_name,
                            "remaining": allowance.get("counter"),
                            "units": allowance.get("units"),
                            "days_to_expire": allowance.get("toEnd"),
                            "type": allowance.get(
                                "offer",
                                {},
                            ).get("domainType"),
                        }

                        usage["allowances"].append(
                            allowance_data
                        )

                        if allowance_name:
                            usage["allowance_summary"][
                                allowance_name
                            ] = allowance_data

            usage_by_msisdn[msisdn] = usage

        return {
            "services_response": services_response,
            "mobile_services_count": len(menu_items),
            "services": entities,
            "usage_by_msisdn": usage_by_msisdn,
            "last_successful_sync": datetime.now(UTC),
            "api_status": "Connected",
            "service_by_msisdn": service_by_msisdn,
            "accounts": accounts,
            "primary_account": next(
                (
                    account
                    for account in accounts
                    if account.get("primary")
                ),
                {},
            ),
        }