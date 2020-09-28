# Backends SLI

## SLIWorkflowLatency

This SLI shows the latency for each workflow considering different buckets:

- `{component}_workflows_latency_bucket_{bucket}` shows duration of successful workflows per Thoth component for different selected bucket.

![SLIWorkflowLatency](https://raw.githubusercontent.com/thoth-station/slo-reporter/master/thoth/slo_reporter/sli_backends/SLIWorkflowLatency.png)

## SLIWorkflowQuality

This SLI shows the quality for each workflow evaluated as percentage of successfull workflows per component, therefore three queries are requested:

- `{component}_workflows_succeeded` shows percentages of successful workflows per Thoth component.

- `{component}_workflows_failed` shows percentages of failed workflows per Thoth component.

- `{component}_workflows_error` shows percentages of workflows in error stage per Thoth component.

![SLIWorkflowQuality](https://raw.githubusercontent.com/thoth-station/slo-reporter/master/thoth/slo_reporter/sli_backends/SLIWorkflowQuality.png)

## SLIWorkflowTaskQuality

This SLI shows the quality for each workflow evaluated as percentage of successfull workflow tasks per component, therefore three queries are requested:

- `{component}_workflow_tasks_succeeded` shows percentages of successful workflows per Thoth component.

- `{component}_workflow_tasks_failed` shows percentages of failed workflows per Thoth component.

- `{component}_workflow_tasks_error` shows percentages of workflows in error stage per Thoth component.

![SLIWorkflowTaskQuality](https://raw.githubusercontent.com/thoth-station/slo-reporter/master/thoth/slo_reporter/sli_backends/SLIWorkflowTaskQuality.png)
