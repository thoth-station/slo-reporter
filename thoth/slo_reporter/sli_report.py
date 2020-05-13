#!/usr/bin/env python3
# slo-reporter
# Copyright(C) 2010 Red Hat, Inc.
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

"""This file contains structures of report for each metric."""

import logging
import os
import datetime

_ENVIRONMENT = os.environ["THOTH_ENVIRONMENT"]
_INSTANCE = os.environ["METRICS_EXPORTER_FRONTEND_PROMETHEUS_INSTANCE"]
_LOGGER = logging.getLogger(__name__)


def _add_dashbords(start_time_epoch: datetime.datetime, end_time_epoch: datetime.datetime):
    """Create dashboard link for report."""
    dashboard_name = f"thoth-knowledge-graph-content-metrics-{_ENVIRONMENT}"
    dashboard_url = (
        f"https://grafana.datahub.redhat.com/dashboard/db/{dashboard_name}?"
        + f"refresh=1m&orgId=1&from={start_time_epoch}&to={end_time_epoch}"
    )

    return f"<br> \
            Reference dashboard: {dashboard_url}"


def _metrics_solved_python_packages():
    """Create data for report for Solved python packages."""
    query_labels = f'{{instance="{_INSTANCE}", job="Thoth Metrics ({_ENVIRONMENT}), main_table="python_package_version"}}'

    return {
        "query": f"thoth_graphdb_total_main_records{query_labels}"
        + f" - min_over_time(thoth_graphdb_total_main_records{query_labels}[7d])",
        "report_method": _report_python_packages,
    }


def _report_python_packages(learned_packages: float):
    """Create report for Python packages."""
    report = f"<br><br> \
                Thoth solved <strong>{int(learned_packages)} Python Packages </strong> in the last week. \
                <br>"

    return report
