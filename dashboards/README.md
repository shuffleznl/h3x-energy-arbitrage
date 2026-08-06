# Pylontech H3X Energy Dashboard

`pylontech-h3x-energy.yaml` is the default Lovelace dashboard for the optional energy-arbitrage stack.

It shows:

- current and future dynamic electricity prices,
- current optimizer decision and reason,
- planned charge/discharge slots with grid-charge, solar-charge, self-consumption, and export split,
- estimated arbitrage value for today and for the active horizon,
- Shelly/SMA load and solar readings when configured,
- basic PV forecast controls and diagnostics,
- load, solar, and net-grid forecast charts,
- battery power and state-of-charge over time,
- Pylontech H3X Bridge controls and diagnostics.

## Requirements

1. Install `https://github.com/shuffleznl/h3x-bridge` through HACS.
2. Install this `https://github.com/shuffleznl/h3x-energy-arbitrage` repository through HACS.
3. Install `apexcharts-card` from HACS for the dashboard charts.

The dashboard uses ApexCharts for price, dispatch, forecast, power, and SOC history.

## Install The YAML Dashboard

Energy Arbitrage `v0.7.3` and newer packages the dashboard inside the HACS-managed
integration directory. Point Home Assistant directly at that copy so a HACS
upgrade refreshes the dashboard automatically:

```text
config/custom_components/h3x_energy_arbitrage/dashboards/pylontech-h3x-energy.yaml
```

Then add this to `configuration.yaml`:

```yaml
lovelace:
  mode: storage
  dashboards:
    pylontech-h3x-energy:
      mode: yaml
      title: Pylontech H3X Energy
      icon: mdi:battery-charging-70
      show_in_sidebar: true
      filename: custom_components/h3x_energy_arbitrage/dashboards/pylontech-h3x-energy.yaml
```

Restart Home Assistant after changing the dashboard filename. For later Energy
Arbitrage updates, update through HACS and refresh the browser after the
integration files have been replaced.

## Planned Slot Display

The optimizer exposes a full `dispatch_plan` with one row per price interval, including idle rows. The dashboard intentionally hides idle rows in the visible planned-action tables and shows only charge/discharge actions plus the dedicated next charge, next discharge, and periodic full-charge sensors. The full plan is still used by the charts.

Planned values can change when Nord Pool publishes new prices, the battery SOC changes, the house load changes, the SMA/PV forecast changes, or grid-limit sensors update.

## PV And Load Configuration

The dashboard assumes `h3x-energy-arbitrage` `v0.7.0` or newer for the Shelly Pro 3EM, SMA Sunny Boy, and PV forecast entities. If those entities are not configured yet, the cards remain visible and show `unknown` until the arbitrage integration receives valid sensor data.

The **Forecast configuration** card contains the editable PV orientation,
panel-count, panel-Wp, and inverter-limit controls. A forecast source of
`disabled_panel_config` means panel count or panel Wp is still zero. The
**Configure Shelly and SMA source entities** button opens the integration page;
use the integration gear there to select the actual load and PV power entities.

## Entity IDs

The dashboard assumes the default entity IDs created by:

- `pylontech_h3x_bridge`
- `h3x_energy_arbitrage`

For the arbitrage integration, Home Assistant prefixes entities with the device name by default, for example `sensor.pylontech_h3x_energy_arbitrage_decision` and `sensor.pylontech_h3x_energy_arbitrage_price_plan`.

If Home Assistant adds suffixes such as `_2`, or an entity was manually renamed,
edit the dashboard YAML and replace the entity IDs using the values shown in
Developer Tools > States.

Control groups use Home Assistant's built-in `entity-filter` card. Controls
that do not exist in an older companion-integration version, or are unavailable,
are omitted instead of rendering repeated entity-not-found rows.
