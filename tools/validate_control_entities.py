#!/usr/bin/env python3
"""Validate runtime control entities and options-flow compatibility."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "h3x_energy_arbitrage"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    const_source = read(INTEGRATION / "const.py")
    config_flow_source = read(INTEGRATION / "config_flow.py")
    init_source = read(INTEGRATION / "__init__.py")
    coordinator_source = read(INTEGRATION / "coordinator.py")
    sensor_source = read(INTEGRATION / "sensor.py")

    for platform in ("Platform.NUMBER", "Platform.SELECT", "Platform.SWITCH"):
        if platform not in const_source:
            raise AssertionError(f"{platform} missing from PLATFORMS")

    for filename in ("number.py", "select.py", "switch.py"):
        path = INTEGRATION / filename
        if not path.exists():
            raise AssertionError(f"missing {filename}")
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    if "return H3XArbitrageOptionsFlow()" not in config_flow_source:
        raise AssertionError("options flow must use Home Assistant-managed config_entry")
    if "self.config_entry = config_entry" in config_flow_source:
        raise AssertionError("options flow must not assign self.config_entry")
    if "_apply_profile_when_changed" not in config_flow_source:
        raise AssertionError("options flow must apply changed strategy profiles")
    if "add_update_listener(async_options_updated)" not in init_source:
        raise AssertionError("options updates must refresh in place")
    if "async_reload_entry" in init_source:
        raise AssertionError("options changes should not force a full reload")

    for token in (
        "CONF_STRATEGY_PROFILE",
        "STRATEGY_PROFILE_SETTINGS",
        "async_apply_strategy_profile",
        "async_set_option",
        "async_options_updated",
        "terminal_soc_mode",
        "strategy_profile",
        "discharge_power_mode",
        "discharge_spread_price_tolerance",
        "discharge_spread_max_hours",
        "grid_import_power_entity",
        "grid_import_average_power_entity",
        "battery_module_count",
        "battery_module_count_entity",
        "battery_capacity_warning",
        "battery_capacity_unconfirmed",
        "_power_state_w",
        "_shape_discharge_decision",
        "_battery_configuration",
    ):
        if token not in coordinator_source and token not in const_source:
            raise AssertionError(f"{token} missing from control wiring")

    if 'key="reason"' not in sensor_source:
        raise AssertionError("decision reason sensor is missing")
    if "CONF_BATTERY_CAPACITY_KWH: 20.0" in const_source:
        raise AssertionError("old 20 kWh scaffold capacity must not be the default")
    if "FORCE_H3_MODULE_CAPACITY_KWH = 5.12" not in const_source:
        raise AssertionError("Force H3 module capacity constant is missing")
    if 'key="discharge_power_mode"' not in read(INTEGRATION / "select.py"):
        raise AssertionError("discharge power mode select is missing")
    number_source = read(INTEGRATION / "number.py")
    for token in (
        "battery_module_count",
        "discharge_spread_price_tolerance",
        "discharge_spread_max_hours",
    ):
        if token not in number_source:
            raise AssertionError(f"{token} number control is missing")


if __name__ == "__main__":
    main()
