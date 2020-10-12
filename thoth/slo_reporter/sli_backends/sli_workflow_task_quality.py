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

"""This file contains class for Workflow Task Quality SLI."""

import logging
import os
import datetime

import numpy as np

from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration


_LOGGER = logging.getLogger(__name__)


class SLIWorkflowTaskQuality(SLIBase):
    """This class contains functions for Workflow TaskQuality SLI (Thoth components)."""

    _SLI_NAME = "workflow_task_quality"

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.sli_columns = [c for c in self.configuration.registered_workflow_tasks]
        self.total_columns = self.default_columns + self.sli_columns

    def _aggregate_info(self):
        """Aggregate info required for workflow_task_quality SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._create_inputs_for_df_sli,
        }

    def _query_sli(self) -> List[str]:
        """Aggregate queries for workflow_task_quality SLI Report."""
        queries = {}
        for component in self.configuration.registered_workflow_tasks:
            result = self._aggregate_queries(component=component)
            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    def _aggregate_queries(self, component: str):
        """Aggregate component queries."""
        instance = self.configuration.registered_workflow_tasks[component]['instance']
        name = self.configuration.registered_workflow_tasks[component]['name']

        query_labels_workflows_s = f'{{instance="{instance}", name="{name}", status="Succeeded"}}'
        query_labels_workflows_f = f'{{instance="{instance}", name="{name}", status="Failed"}}'
        query_labels_workflows_e = f'{{instance="{instance}", name="{name}", status="Error"}}'

        return {
            f"{component}_workflow_tasks_succeeded": {
                "query": f"argo_workflows_task_status_counter{query_labels_workflows_s}",
                "requires_range": True,
                "type": "average",
            },
            f"{component}_workflow_tasks_failed": {
                "query": f"argo_workflows_task_status_counter{query_labels_workflows_f}",
                "requires_range": True,
                "type": "average",
            },
            f"{component}_workflow_tasks_error": {
                "query": f"argo_workflows_task_status_counter{query_labels_workflows_e}",
                "requires_range": True,
                "type": "average",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for component_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for component in self.configuration.registered_workflow_tasks:
            service_metrics = {}
            html_inputs[component] = {}

            for metric, value in sli.items():

                if component in metric:
                    service_metrics[metric] = value

            number_workflow_tasks_succeeded = sli[f"{component}_workflow_tasks_succeeded"]
            number_workflow_tasks_failed = sli[f"{component}_workflow_tasks_failed"]
            number_workflow_tasks_error = sli[f"{component}_workflow_tasks_error"]

            obtained_value = 3
            if service_metrics[f"{component}_workflow_tasks_succeeded"] == "ErrorMetricRetrieval":
                number_workflow_tasks_succeeded = 0
                obtained_value -= 1

            if service_metrics[f"{component}_workflow_tasks_failed"] == "ErrorMetricRetrieval":
                number_workflow_tasks_failed = 0
                obtained_value -= 1

            if service_metrics[f"{component}_workflow_tasks_error"] == "ErrorMetricRetrieval":
                number_workflow_tasks_error = 0
                obtained_value -= 1

            if not obtained_value:
                html_inputs[component]["value"] = np.nan

            else:
                total_workflow_tasks = (
                    int(number_workflow_tasks_succeeded) + int(number_workflow_tasks_failed) + int(number_workflow_tasks_error)
                )

                if int(number_workflow_tasks_succeeded) > 0:

                    if total_workflow_tasks > 0:
                        successfull_percentage = (int(number_workflow_tasks_succeeded) / total_workflow_tasks) * 100
                    else:
                        successfull_percentage = 100

                    html_inputs[component]["value"] = abs(round(successfull_percentage, 3))

                else:
                    html_inputs[component]["value"] = 0


        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for solver_quality SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        report = HTMLTemplates.thoth_workflows_task_quality_template(html_inputs=html_inputs)

        return report

    def _create_inputs_for_df_sli(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> Dict[str, Any]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        parameters = locals()
        parameters.pop("self")

        output = self._create_default_inputs_for_df_sli(**parameters)

        return output
