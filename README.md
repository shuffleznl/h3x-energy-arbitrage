# Pylontech H3X Energy Arbitrage

Home Assistant custom integration for Nord Pool driven charge/discharge decisions for a Pylontech Force H3X system.

This repository contains one HACS integration:

| Integration | Domain | Purpose |
| --- | --- | --- |
| Pylontech H3X Energy Arbitrage | `h3x_energy_arbitrage` | Ingest Nord Pool prices, compute battery arbitrage decisions, and optionally control Force H3X Bridge entities. |

## Requirements

- Home Assistant `2024.6.0` or newer.
- HACS.
- Nord Pool integration configured in Home Assistant.
- Force H3X Bridge installed from `https://github.com/shuffleznl/force-h3x-bridge`.

The controller calls the Nord Pool `get_price_indices_for_date` service, reads the Force H3X Bridge sensors, and writes the Force H3X Bridge EMS mode and charge/discharge power entities when automatic control is enabled.

## HACS Installation

1. In HACS, add `https://github.com/shuffleznl/h3x-energy-arbitrage` as a custom repository of type **Integration**.
2. Install **Pylontech H3X Energy Arbitrage**.
3. Restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Add **Pylontech H3X Energy Arbitrage** and review the detected Nord Pool area and Force H3X Bridge entity IDs.

## Safe First Run

Set **Enable automatic control** to off for the first run. The integration will still compute and expose decisions, prices, planned charge/discharge energy, and estimated value, but it will not write to the H3X entities.

After the decision sensors look correct, enable automatic control from the integration options.

## Default Controlled Entities

| Purpose | Default entity |
| --- | --- |
| EMS mode | `select.force_h3x_bridge_ems_mode` |
| Charge/discharge power | `number.force_h3x_bridge_charge_discharge_power_ref` |
| Battery SOC | `sensor.force_h3x_bridge_battery_soc` |
| House load | `sensor.force_h3x_bridge_load_power` |
| BMS temperature | `sensor.force_h3x_bridge_bms_temperature` |
| Charge SOC limit | `number.force_h3x_bridge_charge_limit_soc` |
| Discharge SOC limit | `number.force_h3x_bridge_discharge_limit_soc_eps` |

## Exposed Sensors

- `sensor.h3x_energy_arbitrage_decision`
- `sensor.h3x_energy_arbitrage_target_power`
- `sensor.h3x_energy_arbitrage_target_power_percent`
- `sensor.h3x_energy_arbitrage_current_price`
- `sensor.h3x_energy_arbitrage_first_slot_value`
- `sensor.h3x_energy_arbitrage_estimated_savings`
- `sensor.h3x_energy_arbitrage_estimated_savings_today`
- `sensor.h3x_energy_arbitrage_planned_charge_energy`
- `sensor.h3x_energy_arbitrage_planned_discharge_energy`
- `sensor.h3x_energy_arbitrage_price_plan`
- `sensor.h3x_energy_arbitrage_price_resolution`
- `sensor.h3x_energy_arbitrage_price_slots_available`

The `price_plan` sensor carries `price_slots`, `today_slots`, `tomorrow_slots`, and `dispatch_plan` attributes for Lovelace charting.

## Economics And Limits

The optimizer supports:

- 15, 30, and 60 minute price slots,
- configurable battery capacity, minimum SOC, reserve SOC, maximum SOC, and terminal SOC behavior,
- round-trip efficiency,
- cycle cost and minimum margin,
- buy-side and sell-side tariff adders,
- continuous and peak power limits,
- house load aware grid import/export caps,
- BMS temperature guards for LiFePO4 charging.

Default power settings are `11 kW` continuous and `13.8 kW` peak, with peak power only used when the price spread clears the configured extra margin.

## Charging Caveat

This controller writes through Force H3X Bridge. If discharging works but grid charging does not, verify the H3X inverter configuration first: Work Mode `P5` charge/discharge time control or another grid-charge-capable mode, Power from Grid/import limit, charge SOC limit, BMS state, and meter configuration.

## Validation

Run local validation with `uv`:

```powershell
$env:UV_PYTHON_INSTALL_DIR='.uv-python'
uv --cache-dir .uv-cache run --python 3.13 python -m compileall custom_components tools
uv --cache-dir .uv-cache run --python 3.13 python tools/validate_hacs_structure.py
```
