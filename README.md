# Thoth Service Level Objective (SLO) reporter

This is Thoth SLO Reporter to share its achievements and behaviour with the outside world.

## Service Level Indicators

SLI indicators are collected in order to create a final report that is sent out to Thoth Team and Users with the following structure:

### Python World

Python world description of packages/releases from indexes (e.g PyPI, AICoE) to check the knowledge available.

- [SLIPyPIKnowledgeGraph](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_python_knowledge_graph/README.md).

### Thoth Learning

This category contains information about Thoth learning rates for packages information (e.g. solver, security):

- [SLILearning](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_learning/README.md).

### Thoth Knoweldge Graph

This category contains information about Thoth knowledge collected:

- [SLIKnowledgeGraph](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_knowledge_graph/README.md).

### Thoth adviser integrations (e.g. Qeb-Hwt GitHub App, Kebechet)

This part of the report is focused on [Thoth integrations](https://github.com/thoth-station/adviser/blob/master/docs/source/integration.rst) and their use:

- [SLIThothIntegrations](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_thoth_integrations).

### Thoth services

- [SLIKebechet](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_thoth_services/README.md).

### Analytics for User requests (e.g. User-API)

This part of the report is focused on analytics for APIs:

- [SLIUserAPI](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_apis/README.md).

### Backend processes (e.g. Argo workflows) status

This part of the report is focused on status of backend processes (e.g. duration, success, failures):

- [SLIWorkflowLatency](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_backends/README.md).

- [SLIWorkflowQuality](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/sli_backends/README.md).

## Data collection

Data collection for SLO report relies on [prometheus-api-client library](https://github.com/AICoE/prometheus-api-client-python).

All data collected can be sent out by [email](https://github.com/thoth-station/slo-reporter/blob/c55577075ff84ddf8a7a68ad604dd153d1ee53b6/app.py#L228)
on [specific day](https://github.com/thoth-station/slo-reporter/blob/c55577075ff84ddf8a7a68ad604dd153d1ee53b6/thoth/slo_reporter/configuration.py#L112)
and [stored on Ceph](https://github.com/thoth-station/slo-reporter/blob/c55577075ff84ddf8a7a68ad604dd153d1ee53b6/app.py#L129) periodically
to reuse the data for visualization (e.g. using [Superset](https://github.com/apache/incubator-superset)).

## Dev Guide

### Adding a new SLI report

1. Add a repo for a new class under [thoth/slo_reporter](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter) if it doesn't exist for the categories of SLI.
The new class would inherit the base class `SLIBase` from [sli_base.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/sli_base.py).
2. Add an HTML jinja template that is to be included in the report here - [Link](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/static/templates)
3. Add a method to load the template you designed in [sli_template.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/sli_template.py) and passes down the parameters and passes them to the template.
4. The query method can be tested against the Prometheus web UI before being added to the method here - [Link](https://prometheus-dh-prod-monitoring.cloud.datahub.psi.redhat.com/graph)
5. In the class that you created in step 1, add the `aggregate_info` method to return the query, the report, the way data will be stored on Ceph.

```python
    def _aggregate_info(self):
        """Aggregate info required for learning quantities SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._create_inputs_for_df_sli,
        }
```

6. Remember to import the class in [sli_report.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/sli_report.py) and add it to the `REPORT_SLI_CONTEXT` dictionary. The order of the class in `REPORT_SLI_CONTEXT` is the order which the report is populated. The general practice for the adding order of reports is - Python world description of packages/releases from indexes (e.g. PyPI, AICoE), Thoth Learning and Thoth Knoweldge Graph, Thoth adviser integrations (e.g. Qeb-Hwt, Kebechet), analytics for requests (e.g. User-API) and backend processes (e.g. Argo workflows).
7. The HTML report structure can be tested using the command stated below.
8. Create a README.md describing the metrics collected for the SLI.

### Adding a new workflow to be monitored

1. Add env variable for the namespace where the Argo workflow is running (if not existing already) in [configuration.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/configuration.py).
2. In the ``REGISTERED_SERVICES`` dictionary in [configuration.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/configuration.py),
a dictionary with the following info need to be added:

- name of the component that uses Argo workflows;
- entrypoint of the Argo workflow as stated in the template with Workflow object;
- namespace where the Argo workflow runs;

Examples:

```python
REGISTERED_SERVICES = {
    "adviser": {
        "entrypoint": "adviser",
        "namespace": _BACKEND_NAMESPACE,
    },
    "kebechet": {
        "entrypoint": "kebechet-job",
        "namespace": _BACKEND_NAMESPACE,
    },
    "inspection": {
        "entrypoint": "main",
        "namespace": _AMUN_INSPECTION_NAMESPACE,
    },
    "qeb-hwt": {
        "entrypoint": "qeb-hwt",
        "namespace": _BACKEND_NAMESPACE,
    },
    "solver": {
        "entrypoint": 'solve-and-sync',
        "namespace": _MIDDLETIER_NAMESPACE,
    },
}
```

### Testing (dry run)

The following command will open a web browser showing how the report will look like.

```python
DEBUG_LEVEL=1 DRY_RUN=1 pipenv run python3 app.py
```
