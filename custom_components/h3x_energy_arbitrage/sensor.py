"""Sensors for Pylontech H3X energy arbitrage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CURRENCY,
    DEFAULT_CURRENCY,
    DOMAIN,
    NORDPOOL_CONF_CURRENCY,
    NORDPOOL_DOMAIN,
)
from .coordinator import H3XArbitrageCoordinator


MONETARY_SENSOR_KEYS = frozenset(
    {
        "first_slot_value",
        "estimated_savings",
        "estimated_savings_today",
    }
)

UNRECORDED_PLAN_ATTRIBUTES = frozenset(
    {
        "dispatch_plan",
        "price_slots",
        "today_slots",
        "tomorrow_slots",
    }
)


@dataclass(frozen=True, kw_only=True)
class H3XArbitrageSensorDescription(SensorEntityDescription):
    """Describe an arbitrage sensor."""

    value_fn: Callable[[dict[str, Any]], Any]
    extra_fn: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None


def _decision_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Return rich diagnostics for the decision sensor."""
    raw_attributes = dict(data.get("attributes") or {})
    attributes = {
        key: raw_attributes.get(key)
        for key in (
            "area",
            "currency",
            "min_soc",
            "max_soc",
            "capacity_kwh",
            "temperature_guard",
            "control_enabled",
            "nordpool_resolution_minutes",
            "normal_max_soc",
            "periodic_full_charge_enabled",
            "periodic_full_charge_due",
            "periodic_full_charge_target_soc",
            "periodic_full_charge_threshold_soc",
            "periodic_full_charge_interval_days",
            "periodic_full_charge_last_at",
            "periodic_full_charge_next_due_at",
        )
    }
    attributes.update(
        {
            "reason": data.get("reason"),
            "current_price": data.get("current_price"),
            "target_power_w": data.get("target_power_w"),
            "target_power_percent": data.get("target_power_percent"),
            "soc": data.get("soc"),
            "load_power_w": data.get("load_power_w"),
            "bms_temperature_c": data.get("bms_temperature_c"),
            "resolution_minutes": data.get("resolution_minutes"),
            "slots_available": data.get("slots_available"),
            "next_slot_start": data.get("next_slot_start"),
            "next_slot_end": data.get("next_slot_end"),
            "estimated_first_slot_value": data.get("estimated_first_slot_value"),
            "estimated_plan_value": data.get("estimated_plan_value"),
            "estimated_today_value": data.get("estimated_today_value"),
            "planned_charge_kwh": data.get("planned_charge_kwh"),
            "planned_discharge_kwh": data.get("planned_discharge_kwh"),
            "applied": data.get("applied"),
            "apply_error": data.get("apply_error"),
            "updated_at": data.get("updated_at"),
        }
    )
    return attributes


def _price_plan_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Return price and dispatch arrays for dashboard charts."""
    attributes = dict(data.get("attributes") or {})
    return {
        "area": attributes.get("area"),
        "currency": attributes.get("currency"),
        "resolution_minutes": data.get("resolution_minutes"),
        "updated_at": data.get("updated_at"),
        "price_slots": attributes.get("price_slots", []),
        "dispatch_plan": attributes.get("dispatch_plan", []),
    }


SENSORS: tuple[H3XArbitrageSensorDescription, ...] = (
    H3XArbitrageSensorDescription(
        key="decision",
        translation_key="decision",
        name="Decision",
        icon="mdi:battery-sync",
        value_fn=lambda data: data.get("action"),
        extra_fn=_decision_attributes,
    ),
    H3XArbitrageSensorDescription(
        key="target_power",
        translation_key="target_power",
        name="Target power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("target_power_w"),
    ),
    H3XArbitrageSensorDescription(
        key="target_power_percent",
        translation_key="target_power_percent",
        name="Target power percent",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("target_power_percent"),
    ),
    H3XArbitrageSensorDescription(
        key="current_price",
        translation_key="current_price",
        name="Current price",
        value_fn=lambda data: data.get("current_price"),
    ),
    H3XArbitrageSensorDescription(
        key="first_slot_value",
        translation_key="first_slot_value",
        name="First slot value",
        device_class=SensorDeviceClass.MONETARY,
        value_fn=lambda data: data.get("estimated_first_slot_value"),
    ),
    H3XArbitrageSensorDescription(
        key="estimated_savings",
        translation_key="estimated_savings",
        name="Estimated savings",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:cash-multiple",
        value_fn=lambda data: data.get("estimated_plan_value"),
    ),
    H3XArbitrageSensorDescription(
        key="estimated_savings_today",
        translation_key="estimated_savings_today",
        name="Estimated savings today",
        device_class=SensorDeviceClass.MONETARY,
        icon="mdi:cash-clock",
        value_fn=lambda data: data.get("estimated_today_value"),
    ),
    H3XArbitrageSensorDescription(
        key="planned_charge_energy",
        translation_key="planned_charge_energy",
        name="Planned charge energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:battery-plus",
        value_fn=lambda data: data.get("planned_charge_kwh"),
    ),
    H3XArbitrageSensorDescription(
        key="planned_discharge_energy",
        translation_key="planned_discharge_energy",
        name="Planned discharge energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:battery-minus",
        value_fn=lambda data: data.get("planned_discharge_kwh"),
    ),
    H3XArbitrageSensorDescription(
        key="price_plan",
        translation_key="price_plan",
        name="Price plan",
        icon="mdi:chart-timeline-variant",
        value_fn=lambda data: data.get("current_price"),
        extra_fn=_price_plan_attributes,
    ),
    H3XArbitrageSensorDescription(
        key="resolution_minutes",
        translation_key="resolution_minutes",
        name="Price resolution",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("resolution_minutes"),
    ),
    H3XArbitrageSensorDescription(
        key="slots_available",
        translation_key="slots_available",
        name="Price slots available",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("slots_available"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: H3XArbitrageCoordinator = entry.runtime_data
    async_add_entities(
        H3XArbitrageSensor(coordinator, entry, description) for description in SENSORS
    )


class H3XArbitrageSensor(CoordinatorEntity[H3XArbitrageCoordinator], SensorEntity):
    """A diagnostic sensor for the arbitrage controller."""

    _unrecorded_attributes = UNRECORDED_PLAN_ATTRIBUTES
    entity_description: H3XArbitrageSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: H3XArbitrageCoordinator,
        entry: ConfigEntry,
        description: H3XArbitrageSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Pylontech H3X Energy Arbitrage",
            "manufacturer": "Local",
            "model": "Nord Pool Optimizer",
        }

    @property
    def native_value(self) -> Any:
        """Return the sensor state."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return dynamic units for price and monetary plan sensors."""
        if self.entity_description.key == "current_price":
            return f"{self._currency_code()}/{UnitOfEnergy.KILO_WATT_HOUR}"
        if self.entity_description.key in MONETARY_SENSOR_KEYS:
            return self._currency_code()
        return self.entity_description.native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return optional attributes."""
        if self.entity_description.extra_fn is None:
            return None
        return self.entity_description.extra_fn(self.coordinator.data or {})

    def _currency_code(self) -> str:
        """Return the active ISO 4217 currency code."""
        data = self.coordinator.data or {}
        attributes = dict(data.get("attributes") or {})
        currency = str(attributes.get("currency") or "").strip().upper()
        if currency and currency != DEFAULT_CURRENCY.upper():
            return currency

        configured = str(
            self._entry.options.get(
                CONF_CURRENCY,
                self._entry.data.get(CONF_CURRENCY, DEFAULT_CURRENCY),
            )
        ).strip().upper()
        if configured and configured != DEFAULT_CURRENCY.upper():
            return configured

        for entry in self.coordinator.hass.config_entries.async_entries(
            NORDPOOL_DOMAIN
        ):
            currency = str(entry.data.get(NORDPOOL_CONF_CURRENCY) or "").strip().upper()
            if currency:
                return currency

        return "EUR"
