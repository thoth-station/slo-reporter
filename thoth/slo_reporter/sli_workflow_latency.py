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

import numpy as np

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class SLIWorkflowLatency(SLIBase):
    """This class contains functions for Workflow Latency SLI (Thoth services)."""

    _SLI_NAME = "component_latency"

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration

    def _aggregate_info(self):
        """Aggregate info required for component_latency SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._create_inputs_for_df_sli,
        }

    def _query_sli(self) -> List[str]:
        """Aggregate queries for component_latency SLI Report."""
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

        query_labels_workflows = f'{{entrypoint="{entrypoint}", namespace="{namespace}"}}'

        return {
            f"{service}_workflows_latency": {
                "query": f"avg(argo_workflow_completion_time{query_labels_workflows}"
                f"- argo_workflow_start_time{query_labels_workflows})",
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
            html_inputs[service] = {}
            number_workflows_latency_seconds = sli[f"{service}_workflows_latency"]

            if number_workflows_latency_seconds != "ErrorMetricRetrieval":
                minutes = number_workflows_latency_seconds / 60
                seconds = number_workflows_latency_seconds % 60
                html_inputs[service]["minutes"] = round(minutes)
                html_inputs[service]["seconds"] = round(seconds)
                html_inputs[service]["value"] = round(minutes)
            else:
                html_inputs[service]["minutes"] = np.nan
                html_inputs[service]["seconds"] = np.nan
                html_inputs[service]["value"] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for component_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        report = HTMLTemplates.thoth_services_latency_template(html_inputs=html_inputs)

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
