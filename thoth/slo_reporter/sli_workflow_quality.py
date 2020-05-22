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

"""This file contains class for Workflow Quality SLI."""

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

REGISTERED_SERVICES = ["adviser", "solver", "inspection"]


class SLIWorkflowQuality(SLIBase):
    """This class contains functions for Workflow Quality SLI (Thoth services)."""

    _SLI_NAME = "component_quality"

    def _aggregate_info(self):
        """"Aggregate info required for solver_quality SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for solver_quality SLI Report."""
        queries = {}
        for service in REGISTERED_SERVICES:
            result = self._aggregate_queries(service=service)
            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    @staticmethod
    def _aggregate_queries(service: str):
        """Aggregate service queries."""
        query_labels_reports = f'{{instance="{_INSTANCE}", result_type="{service}"}}'
        query_labels_workflows_f = f'{{instance="{_INSTANCE}", \
            label_selector="component={service}", \
                job="Thoth Metrics ({Configuration._ENVIRONMENT})", workflow_status="Failed"}}'
        query_labels_workflows_e = f'{{instance="{_INSTANCE}", \
            label_selector="component={service}", \
                job="Thoth Metrics ({Configuration._ENVIRONMENT})", workflow_status="Error"}}'

        return {
            f"{service}_reports": f"delta(\
                thoth_ceph_results_number{query_labels_reports}[{Configuration._INTERVAL}])",
            f"{service}_avg_workflows_failed": f"avg_over_time(\
                thoth_workflows_status{query_labels_workflows_f}[{Configuration._INTERVAL}])",
            f"{service}_avg_workflows_error": f"avg_over_time(\
                thoth_workflows_status{query_labels_workflows_e}[{Configuration._INTERVAL}])",
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for solver_quality SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for service in REGISTERED_SERVICES:
            service_metrics = {}
            for metric, value in sli.items():
                if service in metric:
                    service_metrics[metric] = value

            if all([v for v in service_metrics.values()]):
                total_workflows = (
                    int(sli[f"{service}_reports"])
                    + int(sli[f"{service}_avg_workflows_failed"])
                    + int(sli[f"{service}_avg_workflows_error"])
                )
                if total_workflows:
                    successfull_percentage = (
                        (
                            int(sli[f"{service}_reports"])
                            - int(sli[f"{service}_avg_workflows_failed"])
                            - int(sli[f"{service}_avg_workflows_error"])
                        )
                        / total_workflows
                    ) * 100

                html_inputs[service] = round(successfull_percentage, 3)

            else:

                html_inputs[service] = "Nan"

        report = HTMLTemplates.thoth_services_template(html_inputs=html_inputs)
        return report
