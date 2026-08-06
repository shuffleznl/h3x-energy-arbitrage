#!/usr/bin/env python3
"""Validate the Energy Arbitrage dashboard wiring and packaging."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboards" / "pylontech-h3x-energy.yaml"
PACKAGED_DASHBOARD = (
    ROOT
    / "custom_components"
    / "h3x_energy_arbitrage"
    / "dashboards"
    / "pylontech-h3x-energy.yaml"
)
REMOVED_DASHBOARD = ROOT / "dashboards" / (
    "pylontech-h3x-energy-" + "plot" + "ly.yaml"
)


def read(path: Path) -> str:
    """Read a UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def require(source: str, token: str, label: str) -> None:
    """Require a token in source text."""
    if token not in source:
        raise AssertionError(f"{label} missing {token!r}")


def reject(source: str, token: str, label: str) -> None:
    """Reject a token in source text."""
    if token.lower() in source.lower():
        raise AssertionError(f"{label} still contains {token!r}")


def main() -> None:
    """Run dashboard checks."""
    if not DASHBOARD.exists():
        raise AssertionError("default energy dashboard is missing")
    if not PACKAGED_DASHBOARD.exists():
        raise AssertionError("HACS-packaged energy dashboard is missing")
    if REMOVED_DASHBOARD.exists():
        raise AssertionError("secondary dashboard variant must be removed")

    dashboard = read(DASHBOARD)
    if read(PACKAGED_DASHBOARD) != dashboard:
        raise AssertionError("repository and HACS-packaged dashboards differ")
    dashboards_readme = read(ROOT / "dashboards" / "README.md")
    root_readme = read(ROOT / "README.md")
    combined_docs = dashboards_readme + "\n" + root_readme

    for token in (
        "plot" + "ly",
        "custom:plot" + "ly",
        "pylontech-h3x-energy-plot" + "ly",
    ):
        reject(dashboard, token, "dashboard")
        reject(combined_docs, token, "dashboard docs")

    for token in (
        "select.pylontech_h3x_energy_arbitrage_pv_orientation",
        "number.pylontech_h3x_energy_arbitrage_pv_panel_count",
        "number.pylontech_h3x_energy_arbitrage_pv_panel_wp_rating",
        "number.pylontech_h3x_energy_arbitrage_pv_inverter_limit",
        "sensor.pylontech_h3x_energy_arbitrage_home_load_power",
        "sensor.pylontech_h3x_energy_arbitrage_solar_power",
        "sensor.pylontech_h3x_energy_arbitrage_forecast_load_power",
        "sensor.pylontech_h3x_energy_arbitrage_forecast_solar_power",
        "sensor.pylontech_h3x_energy_arbitrage_planned_grid_charge_energy",
        "sensor.pylontech_h3x_energy_arbitrage_planned_solar_charge_energy",
        "sensor.pylontech_h3x_energy_arbitrage_planned_self_consumption_energy",
        "sensor.pylontech_h3x_energy_arbitrage_planned_battery_export_energy",
        "sensor.pylontech_h3x_energy_arbitrage_forecast_load_energy",
        "sensor.pylontech_h3x_energy_arbitrage_forecast_solar_energy",
        "load_forecast",
        "solar_forecast",
        "net_grid_without_battery_w",
        "net_grid_with_battery_w",
        "grid_charge_kwh",
        "solar_charge_kwh",
        "self_consumption_kwh",
        "battery_export_kwh",
        "title: Forecast configuration",
        "Configure Shelly and SMA source entities",
        "/config/integrations/integration/h3x_energy_arbitrage",
        "disabled_panel_config",
        "type: entity-filter",
        "state_not:",
        "show_empty: false",
        "number.pylontech_h3x_bridge_charge_discharge_power_ref",
        "number.pylontech_h3x_bridge_discharge_limit_soc_eps",
    ):
        require(dashboard, token, "dashboard")

    reject(dashboard, "title: Forecast diagnostics", "dashboard")

    require(dashboards_readme, "`v0.7.0` or newer", "dashboard README")
    require(
        dashboards_readme,
        "custom_components/h3x_energy_arbitrage/dashboards/",
        "dashboard README",
    )
    require(
        root_readme,
        "config/custom_components/h3x_energy_arbitrage/dashboards/",
        "root README",
    )


if __name__ == "__main__":
    main()
