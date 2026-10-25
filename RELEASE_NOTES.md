# Energy Arbitrage 0.7.6

- Recheck bridge ownership before and after each awaited EMS/SOC/power service call, including takeover inside service dispatch.
- Yield cleanly to manual/weather control without logging an expected takeover as a failed dispatch; clear command caches before resuming. Genuine service failures remain visible when no override is active.
- Separate control intent from measured charging confirmation in both dashboards. Show the last competing entity and actual Modbus-command failure.
- Require H3X Bridge 0.4.2. CI tests real Home Assistant entity services, authenticated manual actions, takeover races and dashboard attributes.

Update H3X Bridge to 0.4.2 alongside this integration, then restart Home Assistant. Refresh an imported storage-mode dashboard from `custom_components/h3x_energy_arbitrage/dashboards/pylontech-h3x-energy.yaml`; YAML-mode dashboards referencing the packaged file follow HACS updates. Existing configuration and entity IDs are preserved.

Matching register read-back does not establish physical charging. No physical inverter was connected during validation.
