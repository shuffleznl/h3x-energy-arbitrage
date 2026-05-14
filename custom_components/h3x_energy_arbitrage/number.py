"""Number controls for Pylontech H3X energy arbitrage."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_PERIODIC_FULL_CHARGE_INTERVAL_DAYS,
    CONF_PERIODIC_FULL_CHARGE_TARGET_SOC,
    CONF_PERIODIC_FULL_CHARGE_THRESHOLD_SOC,
    DOMAIN,
)
from .coordinator import H3XArbitrageCoordinator


@dataclass(frozen=True, kw_only=True)
class H3XArbitrageNumberDescription(NumberEntityDescription):
    """Describe an arbitrage number control."""

    option_key: str


NUMBERS: tuple[H3XArbitrageNumberDescription, ...] = (
    H3XArbitrageNumberDescription(
        key="periodic_full_charge_interval_days",
        translation_key="periodic_full_charge_interval_days",
        name="Periodic full-charge interval",
        icon="mdi:calendar-clock",
        native_min_value=1.0,
        native_max_value=90.0,
        native_step=1.0,
        native_unit_of_measurement=UnitOfTime.DAYS,
        option_key=CONF_PERIODIC_FULL_CHARGE_INTERVAL_DAYS,
    ),
    H3XArbitrageNumberDescription(
        key="periodic_full_charge_target_soc",
        translation_key="periodic_full_charge_target_soc",
        name="Periodic full-charge target SOC",
        icon="mdi:battery-charging-100",
        native_min_value=95.0,
        native_max_value=100.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
        option_key=CONF_PERIODIC_FULL_CHARGE_TARGET_SOC,
    ),
    H3XArbitrageNumberDescription(
        key="periodic_full_charge_threshold_soc",
        translation_key="periodic_full_charge_threshold_soc",
        name="Periodic full-charge threshold SOC",
        icon="mdi:battery-check",
        native_min_value=90.0,
        native_max_value=100.0,
        native_step=1.0,
        native_unit_of_measurement=PERCENTAGE,
        option_key=CONF_PERIODIC_FULL_CHARGE_THRESHOLD_SOC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number controls from a config entry."""
    coordinator: H3XArbitrageCoordinator = entry.runtime_data
    async_add_entities(
        H3XArbitrageNumber(coordinator, entry, description)
        for description in NUMBERS
    )


class H3XArbitrageNumber(CoordinatorEntity[H3XArbitrageCoordinator], NumberEntity):
    """A runtime number control for the arbitrage optimizer."""

    entity_description: H3XArbitrageNumberDescription
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: H3XArbitrageCoordinator,
        entry: ConfigEntry,
        description: H3XArbitrageNumberDescription,
    ) -> None:
        """Initialize the number control."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Pylontech H3X Energy Arbitrage",
            "manufacturer": "Local",
            "model": "Nord Pool Optimizer",
        }

    @property
    def native_value(self) -> float | None:
        """Return the current option value."""
        return float(self.coordinator._option(self.entity_description.option_key))

    async def async_set_native_value(self, value: float) -> None:
        """Update the number option."""
        await self.coordinator.async_set_option(
            self.entity_description.option_key,
            float(value),
        )
        self.async_write_ha_state()
