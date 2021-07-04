#!/usr/bin/env python3
# slo-reporter
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

"""This file contains class for Workflow Quality SLI."""

import logging
import datetime

import numpy as np
import pandas as pd

from typing import Dict, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration
from thoth.slo_reporter.utils import retrieve_thoth_sli_from_ceph, evaluate_change


_LOGGER = logging.getLogger(__name__)


class SLIWorkflowQuality(SLIBase):
    """This class contains functions for Workflow Quality SLI (Thoth components)."""

    _SLI_NAME = "component_quality"

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.sli_columns = [c for c in self.configuration.registered_workflows]
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns

    def _query_sli(self) -> Dict[str, Any]:
        """Aggregate queries for component_quality SLI Report."""
        queries = {}
        for component in self.configuration.registered_workflows:
            result = self._aggregate_queries(component=component)
            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    def _aggregate_queries(self, component: str):
        """Aggregate component queries."""
        instance = self.configuration.registered_workflows[component]["instance"]
        name = self.configuration.registered_workflows[component]["name"]

        query_labels_workflows_s = f'{{instance="{instance}", name="{name}", status="Succeeded"}}'
        query_labels_workflows_f = f'{{instance="{instance}", name="{name}", status="Failed"}}'
        query_labels_workflows_e = f'{{instance="{instance}", name="{name}", status="Error"}}'

        return {
            f"{component}_workflows_succeeded": {
                "query": f"argo_workflows_status_counter{query_labels_workflows_s}",
                "requires_range": True,
                "type": "average",
            },
            f"{component}_workflows_failed": {
                "query": f"argo_workflows_status_counter{query_labels_workflows_f}",
                "requires_range": True,
                "type": "average",
            },
            f"{component}_workflows_error": {
                "query": f"argo_workflows_status_counter{query_labels_workflows_e}",
                "requires_range": True,
                "type": "average",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for component_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs: Dict[str, Any] = {}

        for component in self.configuration.registered_workflows:
            service_metrics = {}
            html_inputs[component] = {}

            for metric, value in sli.items():

                if component in metric:
                    service_metrics[metric] = value

            number_workflows_succeeded = sli[f"{component}_workflows_succeeded"]
            number_workflows_failed = sli[f"{component}_workflows_failed"]
            number_workflows_error = sli[f"{component}_workflows_error"]

            obtained_value = 3
            if service_metrics[f"{component}_workflows_succeeded"] == "ErrorMetricRetrieval":
                number_workflows_succeeded = 0
                obtained_value -= 1

            if service_metrics[f"{component}_workflows_failed"] == "ErrorMetricRetrieval":
                number_workflows_failed = 0
                obtained_value -= 1

            if service_metrics[f"{component}_workflows_error"] == "ErrorMetricRetrieval":
                number_workflows_error = 0
                obtained_value -= 1

            if not obtained_value:
                html_inputs[component]["value"] = np.nan

            else:
                total_workflows = (
                    int(number_workflows_succeeded) + int(number_workflows_failed) + int(number_workflows_error)
                )

                if int(number_workflows_succeeded) > 0:

                    if total_workflows > 0:
                        successfull_percentage = (int(number_workflows_succeeded) / total_workflows) * 100
                    else:
                        successfull_percentage = 100

                    html_inputs[component]["value"] = abs(round(successfull_percentage, 3))

                else:
                    html_inputs[component]["value"] = 0

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for workflow quality SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        last_week_data = pd.DataFrame()

        if not self.configuration.dry_run:
            sli_path = f"{self._SLI_NAME}/{self._SLI_NAME}-{self.configuration.last_week_time}.csv"
            last_week_data = retrieve_thoth_sli_from_ceph(self.configuration.ceph_sli, sli_path, self.total_columns)

        for component in self.configuration.registered_workflows:
            if not last_week_data.empty:
                old_value = last_week_data[component].values[0]
                change = evaluate_change(old_value=old_value, new_value=html_inputs[component]["value"])  # type: ignore

                html_inputs[component]["change"] = change  # type: ignore

        report = HTMLTemplates.thoth_workflows_quality_template(html_inputs=html_inputs)

        return report

    def _process_results_to_be_stored(
        self,
        sli: Dict[str, Any],
        datetime: datetime.datetime,
        timestamp: datetime.datetime,
    ) -> Dict[str, Any]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        parameters = locals()
        parameters.pop("self")

        output = self._create_default_inputs_for_df_sli(**parameters)

        return output
