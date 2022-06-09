#!/usr/bin/env python3
# thoth-slo-reporter
# Copyright(C) 2020, 2021 Francesco Murdaca
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Configuration of SLO-reporter."""

import logging
import os
import datetime

from prometheus_client import CollectorRegistry, Gauge
from thoth.common.enums import ThothAdviserIntegrationEnum

from thoth.storages import CephStore

from typing import Optional

_LOGGER = logging.getLogger(__name__)


class Configuration:
    """Configuration of SLO-reporter."""

    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, number_days: int, dry_run: bool):
        """Initialize SLI Configuration."""
        if not start_time:
            raise Exception("Start time date has not been defined!")

        self.start_time = start_time
        self.end_time = end_time
        self.last_week_time = str((self.end_time - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
        self.number_days = number_days
        self.dry_run = dry_run

        self.start_time_epoch = int(self.start_time.timestamp() * 1000)
        self.end_time_epoch = int(self.end_time.timestamp() * 1000)

        if dry_run:
            # Thoth
            self.environment = "dry_run"
            self.backend_namespace = "thoth-dry-run"
            self.middletier_namespace = "thoth-dry-run"
            self.amun_inspection_namespace = "thoth-dry-run"
            self.instance = "dry_run"
            self.instance_wc_backend = "dry_run"
            self.instance_wc_middletier = "dry_run"
            self.instance_wc_amun_inspection = "dry_run"
            self.ceph_sli = "dry_run"

        if not dry_run:

            # Thoth
            self.instance = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_INFRA"]
            self.instance_wc_backend = os.environ["PROMETHEUS_INSTANCE_WORKFLOW_CONTROLLER_BACKEND"]
            self.instance_wc_middletier = os.environ["PROMETHEUS_INSTANCE_WORKFLOW_CONTROLLER_MIDDLETIER"]
            self.instance_wc_amun_inspection = os.environ["PROMETHEUS_INSTANCE_WORKFLOW_CONTROLLER_AMUN_INSPECTION"]

            self.environment = os.environ["THOTH_DEPLOYMENT_NAME"]
            self.deployment_name = os.environ["THOTH_DEPLOYMENT_NAME"]
            self.backend_namespace = os.environ["THOTH_BACKEND_NAMESPACE"]
            self.middletier_namespace = os.environ["THOTH_MIDDLETIER_NAMESPACE"]
            self.amun_inspection_namespace = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]

            # Email server variables smtp
            self.server_host = os.environ["SMTP_SERVER"]
            self.server_host_port = int(os.getenv("SMTP_SERVER_PORT", 587))
            self.smtp_username = os.getenv("SMTP_SERVER_USERNAME")
            self.smtp_password = os.getenv("SMTP_SERVER_PASSWORD")
            self.sender_address = os.environ["EMAIL_SENDER"]
            self.address_recipients = os.environ["EMAIL_RECIPIENTS"]
            self.using_tls = bool(int(os.getenv("THOTH_SLO_REPORTER_USING_SMTP_TLS", 0)))

            # Prometheus and Thanos
            self.pushgateway_endpoint = os.environ["PROMETHEUS_PUSHGATEWAY_URL"]
            self.prometheus_registry = CollectorRegistry()

            self.thoth_weekly_sli = Gauge(
                "thoth_sli_weekly",
                "Weekly Thoth Service Level Indicators",
                ["sli_type", "metric_name", "env"],
                registry=self.prometheus_registry,
            )

            self.thanos_url = os.environ["THANOS_ENDPOINT"]
            self.thanos_token = os.environ["THANOS_ACCESS_TOKEN"]

            # Ceph
            self.public_ceph_bucket = os.getenv("THOTH_PUBLIC_CEPH_BUCKET")
            self.ceph_bucket_prefix = os.environ["THOTH_CEPH_BUCKET_PREFIX"]
            self.ceph_sli = _connect_to_ceph(self.ceph_bucket_prefix, self.environment)  # type: ignore

        # Grafana
        self.grafana_reference_base_url = os.getenv(
            "GRAFANA_DASHBOARD_BASE_URL",
            "https://grafana.operate-first.cloud/",
        )

        # Superset
        self.superset_dashboard_url = os.getenv(
            "SUPERSET_DASHBOARD_URL",
            "https://superset.operate-first.cloud/",
        )

        # TODO: Adjust logic to evaluate metrics not to maintain list of components
        # Registered components (Argo workflows)
        self.registered_workflows = {
            "adviser": {"name": "adviser", "instance": self.instance_wc_backend},
            "kebechet": {"name": "kebechet", "instance": self.instance_wc_backend},
            "inspection": {"name": "main", "instance": self.instance_wc_amun_inspection},
            "package_extract": {"name": "package-extract", "instance": self.instance_wc_middletier},
            "provenance_checker": {"name": "provenance-checker", "instance": self.instance_wc_backend},
            "revsolver": {"name": "revsolver", "instance": self.instance_wc_middletier},
            "security": {"name": "security-indicator", "instance": self.instance_wc_middletier},
            "solver": {"name": "solver", "instance": self.instance_wc_middletier},
        }

        self.registered_workflow_tasks = {
            "adviser": {"name": "adviser", "instance": self.instance_wc_backend},
            "package_extract": {"name": "package-extract", "instance": self.instance_wc_middletier},
            "provenance_checker": {"name": "provenance-checker", "instance": self.instance_wc_backend},
            "solver": {"name": "solver", "instance": self.instance_wc_middletier},
            "revsolver": {"name": "revsolver", "instance": self.instance_wc_middletier},
            "si_download_package": {"name": "download-package", "instance": self.instance_wc_middletier},
            "si_bandit": {"name": "si-bandit", "instance": self.instance_wc_middletier},
            "si_cloc": {"name": "si-cloc", "instance": self.instance_wc_middletier},
        }

        integrations = []

        for thoth_integration in ThothAdviserIntegrationEnum._member_names_:  # type: ignore
            integrations.append(thoth_integration)

        self.thoth_integrations = integrations

        self.buckets = ["5", "10", "30", "60", "120", "180", "300", "600", "900", "+Inf"]

        # Step for query range
        self.step = "1h"

        # Period considered for adviser inputs analysis (in days)
        self.adviser_inputs_analysis_days = 7

        # Service Interval for report
        self.interval = os.getenv("SERVICE_INTERVAL", "7d")

        # Which day of the week do we send the email?
        self.email_day = os.getenv("THOTH_SLO_REPORTER_DAY_SEND_EMAIL", "Friday")


def _connect_to_ceph(ceph_bucket_prefix: str, environment: str, bucket: Optional[str] = None) -> CephStore:
    """Connect to Ceph to store SLI metrics for Thoth."""
    prefix = _get_sli_metrics_prefix(ceph_bucket_prefix=ceph_bucket_prefix, environment=environment)
    ceph = CephStore(prefix=prefix, bucket=bucket)
    ceph.connect()
    return ceph


def _get_sli_metrics_prefix(ceph_bucket_prefix: str, environment: str) -> str:
    """Get prefix where sli metrics are stored.

    This configuration matches sli report classes.
    """
    bucket_prefix = ceph_bucket_prefix
    deployment_name = os.environ["THOTH_DEPLOYMENT_NAME"]
    return f"{bucket_prefix}/{deployment_name}/thoth-sli-metrics-{environment}"
