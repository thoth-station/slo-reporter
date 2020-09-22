# Thoth adviser integrations (e.g. Qeb-Hwt GitHub App, Kebechet)

## SLIThothIntegrations

Thoth integrations SLI is selected to have an overview of which integration in Thoth are used the most in order to prioritize next features.

- `"{thoth_integration}_counts_use"` considers how many times has been used in the period selected in the valuation. For example if SLO reporter is run
per day, the value obtained is relative to the number of times a certain Thoth integration is used in that period, therefore it is called `periodic result`.

- `"{thoth_integration}_counts_total"` considers how many times has been used since we started to collect the SLI.
