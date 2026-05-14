# Pylontech H3X Energy Arbitrage

Home Assistant custom integration for Nord Pool driven charge/discharge decisions for a Pylontech Force H3X system.

This repository contains one HACS integration:

| Integration | Domain | Purpose |
| --- | --- | --- |
| Pylontech H3X Energy Arbitrage | `h3x_energy_arbitrage` | Ingest Nord Pool prices, compute battery arbitrage decisions, and optionally control Pylontech H3X Bridge entities. |

## Requirements

- Home Assistant `2024.6.0` or newer.
- HACS.
- Nord Pool integration configured in Home Assistant.
- Pylontech H3X Bridge installed from `https://github.com/shuffleznl/pylontech-fh3x-bridge`.

The controller calls the Nord Pool `get_price_indices_for_date` service, reads the Pylontech H3X Bridge sensors, and writes the Pylontech H3X Bridge EMS mode and charge/discharge power entities when automatic control is enabled.

## HACS Installation

1. In HACS, add `https://github.com/shuffleznl/h3x-energy-arbitrage` as a custom repository of type **Integration**.
2. Install **Pylontech H3X Energy Arbitrage**.
3. Restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Add **Pylontech H3X Energy Arbitrage** and review the detected Nord Pool area and Pylontech H3X Bridge entity IDs.

## Safe First Run

Set **Enable automatic control** to off for the first run. The integration will still compute and expose decisions, prices, planned charge/discharge energy, and estimated value, but it will not write to the H3X entities.

After the decision sensors look correct, enable automatic control from the integration options.

## Default Controlled Entities

| Purpose | Default entity |
| --- | --- |
| EMS mode | `select.pylontech_h3x_bridge_ems_mode` |
| Charge/discharge power | `number.pylontech_h3x_bridge_charge_discharge_power_ref` |
| Battery SOC | `sensor.pylontech_h3x_bridge_battery_soc` |
| House load | `sensor.pylontech_h3x_bridge_load_power` |
| BMS temperature | `sensor.pylontech_h3x_bridge_bms_temperature` |
| Charge SOC limit | `number.pylontech_h3x_bridge_charge_limit_soc` |
| Discharge SOC limit | `number.pylontech_h3x_bridge_discharge_limit_soc_eps` |

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

The `price_plan` sensor is a unitless diagnostic carrier for Lovelace charting. It carries `price_slots` and `dispatch_plan` attributes, and those large chart arrays are excluded from recorder history to keep the Home Assistant database small. Currency values use the resolved Nord Pool ISO 4217 currency code, for example `EUR` or `DKK`.

## Economics And Limits

The optimizer supports:

- 15, 30, and 60 minute price slots,
- configurable battery capacity, minimum SOC, reserve SOC, maximum SOC, and terminal SOC behavior,
- periodic full-charge/top-balance cycle scheduled into the cheapest available slots,
- round-trip efficiency,
- cycle cost and minimum margin,
- buy-side and sell-side tariff adders,
- continuous and peak power limits,
- house load aware grid import/export caps,
- BMS temperature guards for LiFePO4 charging.

Default power settings are `11 kW` continuous and `13.8 kW` peak, with peak power only used when the price spread clears the configured extra margin.

## Periodic Full Charge

LiFePO4 packs are normally happier cycling below 100% SOC, but the BMS may need an occasional full charge for top balancing and SOC calibration. The integration therefore defaults to one 100% target every 7 days, counted complete when the SOC sensor reaches 99%.

When the full-charge interval is due, the optimizer temporarily raises the charge SOC limit to the configured target and adds that energy requirement to the price plan. It still uses Nord Pool pricing, so the extra charge is placed in the cheapest available slot inside the configured horizon instead of at a fixed clock time. After the threshold is reached, the timestamp is stored in Home Assistant storage and the normal maximum SOC limit is restored on the next control pass.

## Charging Caveat

This controller writes through Pylontech H3X Bridge. If discharging works but grid charging does not, verify the H3X inverter configuration first: Work Mode `P5` charge/discharge time control or another grid-charge-capable mode, Power from Grid/import limit, charge SOC limit, BMS state, and meter configuration.

## Validation

Run local validation with `uv`:

```powershell
$env:UV_PYTHON_INSTALL_DIR='.uv-python'
uv --cache-dir .uv-cache run --python 3.13 python -m compileall custom_components tools
uv --cache-dir .uv-cache run --python 3.13 python tools/validate_hacs_structure.py
uv --cache-dir .uv-cache run --python 3.13 python tools/validate_sensor_metadata.py
uv --cache-dir .uv-cache run --python 3.13 python tools/validate_periodic_full_charge.py
```
