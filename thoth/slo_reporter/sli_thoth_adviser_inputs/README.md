# Thoth adviser inputs analysis

## Adviser inputs overview

Thoth Adviser inputs SLIs are selected to have an overview of which inputs are given to Thoth for recommendation.
They all include

- `{thoth_integration}_counts_total` considers how many times has been in the time window considered (e.g. 7 days).

The following adviser inputs are considered at the moment:

- `SLIThothRecommendationsTypesInputs`
- `SLIThothSolversInputs`
- `SLIThothBaseImagesInputs`
- `SLIThothHardwareInputs`

## SLIThothIntegrations

Thoth integrations SLI is selected to have an overview of which integration in Thoth are used the most in order to prioritize next features.

- `{thoth_integration}_counts_use` considers how many times has been used in the period selected in the valuation. For example if SLO reporter is run
per day, the value obtained is relative to the number of times a certain Thoth integration is used in that period, therefore it is called `periodic result`.

- `{thoth_integration}_counts_total` considers how many times has been used since we started to collect the SLI.

![SLIThothIntegrations](https://raw.githubusercontent.com/thoth-station/slo-reporter/master/thoth/slo_reporter/sli_thoth_integrations/SLIThothIntegrations.png)

## SLIThothIntegrationsUsers

Thoth integrations Users SLI is selected to have an overview of number of users per integration in Thoth. (only for Kebechet)
