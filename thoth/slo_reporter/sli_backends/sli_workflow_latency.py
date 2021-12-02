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

"""This file contains class for Workflow Latency SLI."""

import logging
import datetime

import numpy as np
from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class SLIWorkflowLatency(SLIBase):
    """This class contains functions for Workflow Latency SLI (Thoth components)."""

    _SLI_NAME = "component_latency"

    sli_columns = [
        "component",
        "bucket",
        "percentage",
    ]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns

    def _query_sli(self) -> Dict[str, Any]:
        """Aggregate queries for component_latency SLI Report."""
        queries = {}
        for component in self.configuration.registered_workflows:
            result = self._aggregate_queries(component=component)
            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    def _aggregate_queries(self, component: str):
        """Aggregate service queries."""
        instance = self.configuration.registered_workflows[component]["instance"]
        name = self.configuration.registered_workflows[component]["name"]

        queries = {}

        for bucket in self.configuration.buckets:
            query_labels_workflows = f'{{field="{instance}", name="{name}", le="{bucket}"}}'
            queries[f"{component}_workflows_latency_bucket_{bucket}"] = {
                "query": f"argo_workflows_duration_seconds_histogram_bucket{query_labels_workflows}",
                "requires_range": True,
                "type": "latest",
            }
        return queries

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for component_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs: Dict[str, Any] = {}

        for component in self.configuration.registered_workflows:
            html_inputs[component] = {}

            buckets_results = {}
            has_nan = False

            for bucket in self.configuration.buckets:
                number_workflows_latency_seconds_bucket = sli[f"{component}_workflows_latency_bucket_{bucket}"]

                if number_workflows_latency_seconds_bucket != "ErrorMetricRetrieval":
                    buckets_results[bucket] = number_workflows_latency_seconds_bucket
                else:
                    buckets_results[bucket] = np.nan
                    has_nan = True

            if not has_nan:
                for bucket in self.configuration.buckets:
                    if bucket == "+Inf":
                        if buckets_results["+Inf"] > 0:
                            percentage = (buckets_results["+Inf"] - buckets_results["900"]) / buckets_results["+Inf"]
                            html_inputs[component]["+Inf"] = round(percentage * 100, 3)
                        else:
                            html_inputs[component]["+Inf"] = np.nan
                    else:
                        if buckets_results["+Inf"] > 0:
                            percentage = buckets_results[bucket] / buckets_results["+Inf"]
                            html_inputs[component][bucket] = round(percentage * 100, 3)
                        else:
                            html_inputs[component][bucket] = np.nan
            else:
                for bucket in self.configuration.buckets:
                    if bucket == "+Inf":
                        html_inputs[component]["+Inf"] = np.nan
                    else:
                        html_inputs[component][bucket] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for component_latency SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        report = HTMLTemplates.thoth_services_latency_template(
            html_inputs=html_inputs,
            configuration_buckets=self.configuration.buckets,
        )

        return report

    def _process_results_to_be_stored(
        self,
        sli: Dict[str, Any],
        datetime: datetime.datetime,
        timestamp: datetime.datetime,
    ) -> List[Dict[str, Any]]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)
        df_inputs = []

        for component in self.configuration.registered_workflows:
            for bucket in self.configuration.buckets:
                if bucket != "+Inf":
                    df_inputs.append(
                        {
                            "datetime": datetime,
                            "timestamp": timestamp,
                            "component": component,
                            "bucket": bucket,
                            "percentage": html_inputs[component][bucket],  # type: ignore
                        },
                    )

        return df_inputs
