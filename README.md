# Pylontech H3X Energy Arbitrage

Home Assistant custom integration for Nord Pool driven charge/discharge decisions for a Pylontech Force H3X system.

This repository contains one HACS integration:

| Integration | Domain | Purpose |
| --- | --- | --- |
| Pylontech H3X Energy Arbitrage | `h3x_energy_arbitrage` | Ingest Nord Pool prices, compute battery arbitrage decisions, and optionally control Pylontech H3X Bridge entities. |

## Requirements

- Home Assistant `2024.12.0` or newer.
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
| Real-time grid import | `sensor.dsmr_reading_electricity_currently_delivered` |
| Averaged grid import | `sensor.connect_energy_meter_electricity_average` |
| Battery module count | `sensor.pylontech_h3x_bridge_battery_module_count` |
| BMS temperature | `sensor.pylontech_h3x_bridge_bms_temperature` |
| Charge SOC limit | `number.pylontech_h3x_bridge_charge_limit_soc` |
| Discharge SOC limit | `number.pylontech_h3x_bridge_discharge_limit_soc_eps` |

## Exposed Sensors

- `sensor.h3x_energy_arbitrage_decision`
- `sensor.h3x_energy_arbitrage_target_power`
- `sensor.h3x_energy_arbitrage_target_power_percent`
- `sensor.h3x_energy_arbitrage_current_price`
- `sensor.h3x_energy_arbitrage_decision_reason`
- `sensor.h3x_energy_arbitrage_first_slot_value`
- `sensor.h3x_energy_arbitrage_estimated_savings`
- `sensor.h3x_energy_arbitrage_estimated_savings_today`
- `sensor.h3x_energy_arbitrage_planned_charge_energy`
- `sensor.h3x_energy_arbitrage_planned_discharge_energy`
- `sensor.h3x_energy_arbitrage_price_plan`
- `sensor.h3x_energy_arbitrage_price_resolution`
- `sensor.h3x_energy_arbitrage_price_slots_available`

The `price_plan` sensor is a unitless diagnostic carrier for Lovelace charting. It carries `price_slots` and `dispatch_plan` attributes, and those large chart arrays are excluded from recorder history to keep the Home Assistant database small. Currency values use the resolved Nord Pool ISO 4217 currency code, for example `EUR` or `DKK`.

## Runtime Controls

The integration exposes Home Assistant control entities so the strategy can be adjusted without opening the full options form:

- `select.h3x_energy_arbitrage_strategy_profile`: `conservative`, `typical`, `aggressive`, or `custom`.
- `select.h3x_energy_arbitrage_end_of_horizon_soc`: preserve the current SOC by the end of the horizon, or allow discharge down to reserve.
- `select.h3x_energy_arbitrage_discharge_power_mode`: spread discharge over adjacent high-price slots, or keep the maximum economic target power.
- `number.h3x_energy_arbitrage_battery_module_count`: set the installed Force H3 module count when it is not available from a bridge sensor.
- `switch.h3x_energy_arbitrage_periodic_full_charge`: enable or disable the periodic full-charge constraint.
- `number.h3x_energy_arbitrage_periodic_full_charge_interval`, `target_soc`, and `threshold_soc`: tune the periodic full-charge cadence and completion threshold.
- `number.h3x_energy_arbitrage_discharge_spread_price_tolerance` and `discharge_spread_max_hours`: tune how far and how long discharge can be spread.

Strategy profiles apply these tradeoffs:

- `conservative`: preserve current SOC, keep periodic full charge enabled, spread discharge over a wider price band, use a higher profit margin, lower normal maximum SOC, and disable peak power.
- `typical`: balanced default behavior with discharge spread across nearby high-price slots when prices are within 10% of the current expensive slot.
- `aggressive`: prioritize estimated savings by allowing reserve-only end-of-horizon behavior, disabling periodic full-charge forcing, allowing 100% maximum SOC, using maximum economic discharge power, and removing extra profit margin. This is economically aggressive and less battery-conservative.

## Economics And Limits

The optimizer supports:

- 15, 30, and 60 minute price slots,
- Force H3 module-count based battery capacity, minimum SOC, reserve SOC, maximum SOC, and terminal SOC behavior,
- periodic full-charge/top-balance cycle scheduled into the cheapest available slots,
- round-trip efficiency,
- cycle cost and minimum margin,
- buy-side and sell-side tariff adders,
- continuous and peak power limits,
- house load aware grid import/export caps,
- real-time and 5-minute average grid import guards for charging,
- profile-controlled discharge spreading across economically similar expensive slots,
- BMS temperature guards for LiFePO4 charging.

Default power settings are `11 kW` continuous and `13.8 kW` peak, with peak power only used when the price spread clears the configured extra margin. The default grid import limit is `17.5 kW`; set it to `0` in options to disable the import guard.

Charging is not intentionally slowed by the discharge spread controls. The optimizer still charges at the cheapest economic speed, capped by inverter power, BMS temperature, SOC limits, and the grid import limit. When DSMR or averaged import sensors are configured, charging headroom is based on the most conservative available reading and accounts for any already-requested battery charge power to avoid self-throttling during an active charge.

Discharge spreading is a post-optimizer shaping step. In `spread` mode, the selected export energy is averaged across consecutive expensive slots that remain within the configured price tolerance and maximum window. In `max_economic` mode, the raw optimizer setpoint is used.

## Battery Capacity

Force H3 capacity is modeled by module count, not by an arbitrary kWh default. The Pylontech Force H3 datasheet lists each FH10050 module as `5.12 kWh`; one inverter stack supports `2` to `7` modules, so nominal capacity is:

| Modules | Nominal capacity |
| --- | --- |
| 2 | 10.24 kWh |
| 3 | 15.36 kWh |
| 4 | 20.48 kWh |
| 5 | 25.60 kWh |
| 6 | 30.72 kWh |
| 7 | 35.84 kWh |

Your current target system is `6` modules, therefore `30.72 kWh` nominal. The older `20 kWh` default was only a scaffold value and was not read from the inverter or BMS.

The Pylontech Modbus documentation includes a BMS/ESS register for "Module number in series" at offset `0x0036`; with ESS base address `0x1400`, this is register `0x1436` / decimal `5174` on the BMS side. The arbitrage integration does not open its own Modbus connection. Instead, it can consume `sensor.pylontech_h3x_bridge_battery_module_count` if the bridge exposes that value. Until that sensor exists, set the module count manually in the integration options or with the runtime number entity.

Capacity is safety-critical for this optimizer. If the module count is too low, the controller underestimates available energy and may miss profitable discharge/charge windows. If it is too high, it can overestimate energy above reserve and plan charge/discharge energy the physical battery cannot deliver. Existing installs that still have only the old non-multiple capacity value will raise a Home Assistant repair warning until the module count is confirmed.

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
uv --cache-dir .uv-cache run --python 3.13 python tools/validate_control_entities.py
```
