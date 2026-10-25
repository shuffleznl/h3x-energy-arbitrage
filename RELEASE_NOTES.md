# Energy Arbitrage 0.7.5

- Align override/weather controls with H3X Bridge 0.4.1's stable entity IDs and actionable force-charge errors.
- Show charging headroom, grid load excluding the battery, signed register read-back and last-command verification in both dashboard copies.
- Preserve the existing optimization strategy and native layout. Negative references still request charge; inverter/BMS safety limits remain authoritative.
- The sibling bridge runtime suite checks actual Home Assistant registration and every bridge attribute referenced by this dashboard before and after a charge command.

Install H3X Bridge 0.4.1, then restart Home Assistant. Refresh an imported storage-mode dashboard from `custom_components/h3x_energy_arbitrage/dashboards/pylontech-h3x-energy.yaml`; YAML-mode dashboards referencing the packaged file follow HACS updates. Deliberately customized bridge IDs require matching YAML.

Matching register read-back does not establish physical charging. No physical inverter was connected during validation.
