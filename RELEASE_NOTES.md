# Energy Arbitrage 0.7.4

- Yield to H3X Bridge manual charging and KNMI weather reserve, then reset command caches before automatic dispatch resumes.
- Add the new bridge controls to the packaged and repository dashboards.
- Arrange dashboard sections with controls first, usage/savings/power in the middle, and statistics/diagnostics below.
- Update documentation and version metadata. Existing integration and dashboard validators pass.

Install H3X Bridge 0.4.0 for the new controls. Configure KNMI/Shelly/siren entities on the bridge. Refresh an imported storage-mode dashboard from `custom_components/h3x_energy_arbitrage/dashboards/pylontech-h3x-energy.yaml` after the HACS update.
