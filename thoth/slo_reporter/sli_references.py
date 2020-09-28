#!/usr/bin/env python3
# slo-reporter
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

"""This file contains references to be included in the final report."""

import os
import logging
import datetime

from .configuration import Configuration

from .sli_template import HTMLTemplates

_LOGGER = logging.getLogger(__name__)


def _add_dashbords(configuration: Configuration):
    """Create dashboard link for report."""
    start_time_epoch = configuration.start_time_epoch
    end_time_epoch = configuration.end_time_epoch

    html_inputs = {}

    knowledge_graph_dashboard_name = f"thoth-knowledge-graph-content-metrics"
    knowledge_graph_dashboard_url = (
        f"https://grafana.datahub.redhat.com/dashboard/db/{knowledge_graph_dashboard_name}?"
        + f"refresh=1m&orgId=1&from={start_time_epoch}&to={end_time_epoch}&"
        + f"var-instance={configuration.instance}&"
        + f"var-environment={configuration.environment}"
    )
    html_inputs["Thoth Knowledge Graph"] = {
        "url": knowledge_graph_dashboard_url,
        "description": "Dashboard for Thoth Knowledge Graph data stored.",
    }

    sli_slo_dashboard_name = f"thoth-sli-slo"
    sli_slo_dashboard_url = (
        f"https://grafana.datahub.redhat.com/dashboard/db/{sli_slo_dashboard_name}?"
        + f"refresh=1m&orgId=1&from={start_time_epoch}&to={end_time_epoch}"
    )
    html_inputs["Thoth SLI/SLO"] = {"url": sli_slo_dashboard_url, "description": "Dashboard for SLI/SLO for Thoth."}

    sli_slo_dashboard_name = f"thoth-reports"
    sli_slo_dashboard_url = (
        f"https://grafana.datahub.redhat.com/dashboard/db/{sli_slo_dashboard_name}?"
        + f"refresh=1m&orgId=1&from={start_time_epoch}&to={end_time_epoch}"
    )
    html_inputs["Thoth Reports"] = {
        "url": sli_slo_dashboard_url,
        "description": "Dashboard for summary reports created by Thoth reporters components.",
    }
    if configuration.environment == "stage":
        sli_slo_dashboard_name = f"thoth-superset"
        sli_slo_dashboard_url = f"https://superset.datahub.redhat.com/superset/dashboard/17/"
        html_inputs["Thoth Superset"] = {
            "url": sli_slo_dashboard_url,
            "description": "Superset Dashboard for SLI/SLO in time.",
        }

    report = HTMLTemplates.thoth_references_template(html_inputs=html_inputs)
    return report
