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

import numpy as np

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration


_LOGGER = logging.getLogger(__name__)


class SLIWorkflowQuality(SLIBase):
    """This class contains functions for Workflow Quality SLI (Thoth services)."""

    _SLI_NAME = "component_quality"

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration

    def _aggregate_info(self):
        """Aggregate info required for solver_quality SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._create_inputs_for_df_sli,
        }

    def _query_sli(self) -> List[str]:
        """Aggregate queries for solver_quality SLI Report."""
        queries = {}
        for service in self.configuration.registered_services:
            result = self._aggregate_queries(service=service)
            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    def _aggregate_queries(self, service: str):
        """Aggregate service queries."""
        query_labels_reports = f'{{instance="{self.configuration.instance}", result_type="{service}"}}'

        entrypoint = self.configuration.registered_services[service]["entrypoint"]
        namespace = self.configuration.registered_services[service]["namespace"]

        query_labels_workflows_s = f'{{entrypoint="{entrypoint}", namespace="{namespace}", phase="Succeeded"}}'
        query_labels_workflows_f = f'{{entrypoint="{entrypoint}", namespace="{namespace}", phase="Failed"}}'
        query_labels_workflows_e = f'{{entrypoint="{entrypoint}", namespace="{namespace}", phase="Error"}}'

        return {
            f"{service}_workflows_succeeded": {
                "query": f"sum(argo_workflow_status_phase{query_labels_workflows_s})",
                "requires_range": True,
                "type": "average",
            },
            f"{service}_workflows_failed": {
                "query": f"sum(argo_workflow_status_phase{query_labels_workflows_f})",
                "requires_range": True,
                "type": "average",
            },
            f"{service}_workflows_error": {
                "query": f"sum(argo_workflow_status_phase{query_labels_workflows_e})",
                "requires_range": True,
                "type": "average",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for component_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for service in self.configuration.registered_services:
            service_metrics = {}
            html_inputs[service] = {}

            for metric, value in sli.items():

                if service in metric:
                    service_metrics[metric] = value

            number_workflows_succeeded = sli[f"{service}_workflows_succeeded"]
            number_workflows_failed = sli[f"{service}_workflows_failed"]
            number_workflows_error = sli[f"{service}_workflows_error"]

            if "ErrorMetricRetrieval" not in [v for v in service_metrics.values()]:

                total_workflows = (
                    int(number_workflows_succeeded) + int(number_workflows_failed) + int(number_workflows_error)
                )
                if int(number_workflows_succeeded) > 0:

                    successfull_percentage = (int(number_workflows_succeeded) / total_workflows) * 100

                    html_inputs[service]["value"] = abs(round(successfull_percentage, 3))

                else:
                    html_inputs[service]["value"] = 0

            else:
                html_inputs[service]["value"] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for solver_quality SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        report = HTMLTemplates.thoth_services_quality_template(html_inputs=html_inputs)

        return report

    def _create_inputs_for_df_sli(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime
    ) -> Dict[str, Any]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        parameters = locals()
        parameters.pop("self")

        output = self._create_default_inputs_for_df_sli(**parameters)

        return output
