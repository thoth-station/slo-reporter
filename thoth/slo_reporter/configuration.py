#!/usr/bin/env python3
# thoth-slo-reporter
# Copyright(C) 2020 Francesco Murdaca
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

_DAYS_REPORT = 1
_END_TIME = datetime.datetime.utcnow()
_START_TIME = _END_TIME - datetime.timedelta(days=_DAYS_REPORT)

_LOGGER = logging.getLogger(__name__)


class Configuration:
    """Configuration of SLO-reporter."""

    DRY_RUN = bool(int(os.getenv("DRY_RUN", 0)))

    ONLY_STORE_ON_CEPH = bool(int(os.getenv("THOTH_SLO_REPORTER_ONLY_STORE_ON_CEPH", 0)))

    START_TIME = _START_TIME
    END_TIME = _END_TIME
    START_TIME_EPOCH = int(START_TIME.timestamp() * 1000)
    END_TIME_EPOCH = int(END_TIME.timestamp() * 1000)

    if DRY_RUN:
        # Thoth
        _ENVIRONMENT = "dry_run"
        _BACKEND_NAMESPACE = "thoth-dry-run"
        _MIDDLETIER_NAMESPACE = "thoth-dry-run"
        _AMUN_INSPECTION_NAMESPACE = "thoth-dry-run"

    if not DRY_RUN:

        # Email variables
        _SERVER = os.environ["SMTP_SERVER"]
        _SENDER_ADDRESS = os.environ["SENDER_ADDRESS"]
        _ADDRESS_RECIPIENTS = os.environ["EMAIL_RECIPIENTS"]

        # Prometheus and Thanos
        _PUSHGATEWAY_ENDPOINT = os.environ["PROMETHEUS_PUSHGATEWAY_URL"]

        _THANOS_URL = os.environ["THANOS_ENDPOINT"]
        _THANOS_TOKEN = os.environ["THANOS_ACCESS_TOKEN"]

        # Thoth
        _ENVIRONMENT = os.environ["THOTH_ENVIRONMENT"]
        _BACKEND_NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]
        _MIDDLETIER_NAMESPACE = os.environ["THOTH_MIDDLETIER_NAMESPACE"]
        _AMUN_INSPECTION_NAMESPACE = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]

        _PUBLIC_CEPH_BUCKET = os.environ["THOTH_PUBLIC_CEPH_BUCKET"]

        _CEPH_BUCKET_PREFIX = os.environ["THOTH_CEPH_BUCKET_PREFIX"]

    # Registered services (Argo workflows)
    REGISTERED_SERVICES = {
        "adviser": {"entrypoint": "adviser", "namespace": _BACKEND_NAMESPACE},
        "kebechet": {"entrypoint": "kebechet-job", "namespace": _BACKEND_NAMESPACE},
        "inspection": {"entrypoint": "main", "namespace": _AMUN_INSPECTION_NAMESPACE},
        "qeb-hwt": {"entrypoint": "qeb-hwt", "namespace": _BACKEND_NAMESPACE},
        "solver": {"entrypoint": "solve-and-sync", "namespace": _MIDDLETIER_NAMESPACE},
    }

    # Step for query range
    STEP = "2h"

    # Interval for report
    INTERVAL = "7d"


def _get_sli_metrics_prefix() -> str:
    """Get prefix where sli metrics are stored.

    This configuration matches sli report classes.
    """
    bucket_prefix = Configuration._CEPH_BUCKET_PREFIX
    deployment_name = os.environ["THOTH_DEPLOYMENT_NAME"]
    return f"{bucket_prefix}/{deployment_name}/thoth-sli-metrics-{Configuration._ENVIRONMENT}"
