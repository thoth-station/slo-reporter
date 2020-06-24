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

"""This file contains class for Workflow Latency SLI."""

import logging
import os
import datetime

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_INSTANCE = "dry_run"

if not Configuration.DRY_RUN:
    _INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]

_LOGGER = logging.getLogger(__name__)


class SLIWorkflowLatency(SLIBase):
    """This class contains functions for Workflow Latency SLI (Thoth services)."""

    _SLI_NAME = "component_latency"

    def _aggregate_info(self):
        """Aggregate info required for solver_latency SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for solver_latency SLI Report."""
        queries = {}
        for service in Configuration.REGISTERED_SERVICES:
            result = self._aggregate_queries(service=service)
            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    @staticmethod
    def _aggregate_queries(service: str):
        """Aggregate service queries."""
        query_labels_reports = f'{{instance="{_INSTANCE}", result_type="{service}"}}'

        entrypoint = Configuration.REGISTERED_SERVICES[service]["entrypoint"]
        namespace = Configuration.REGISTERED_SERVICES[service]["namespace"]

        query_labels_workflows = f'{{entrypoint="{entrypoint}", namespace="{namespace}"}}'

        return {
            f"{service}_workflows_latency": {
                "query": f"avg(argo_workflow_completion_time{query_labels_workflows} - argo_workflow_start_time{query_labels_workflows})",
                "requires_range": True,
                "type": "average",
            }
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for solver_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for service in Configuration.REGISTERED_SERVICES:
            html_inputs[service] = {}
            number_workflows_latency_seconds = sli[f"{service}_workflows_latency"]

            if number_workflows_latency_seconds != "ErrorMetricRetrieval":
                minutes = number_workflows_latency_seconds / 60
                seconds = number_workflows_latency_seconds % 60
                html_inputs[service]["minutes"] = round(minutes)
                html_inputs[service]["seconds"] = round(seconds)
            else:
                html_inputs[service]["minutes"] = "Nan"
                html_inputs[service]["seconds"] = "Nan"

        report = HTMLTemplates.thoth_services_latency_template(html_inputs=html_inputs)

        return report
