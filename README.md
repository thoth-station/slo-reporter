# Thoth Service Level Objective (SLO) reporter

This is Thoth SLO Reporter to share its achievements and behaviour with the outside world.


### Testing (dry run)

.. code-block:: console

    THOTH_ENVIRONMENT=test DEBUG_LEVEL=1 PROMETHEUS_INSTANCE_USER_API=user-api-thoth-test-core.cloud.paas.psi.redhat.com:80 PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND=metrics-exporter-thoth-test-core.cloud.paas.psi.redhat.com:80 THANOS_ENDPOINT=<thanos_endpoint> THANOS_ACCESS_TOKEN=<thanos_token> PROMETHEUS_PUSHGATEWAY_URL=<pushgateway_url> DRY_RUN=1 pipenv run python3 app.py
