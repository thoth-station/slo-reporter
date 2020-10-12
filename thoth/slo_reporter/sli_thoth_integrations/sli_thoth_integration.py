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

"""This file contains class for Thoth Integrations SLI."""

import logging
import os
import datetime

import numpy as np

from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration

_LOGGER = logging.getLogger(__name__)


class SLIThothIntegrations(SLIBase):
    """This class contain functions for Thoth Integrations SLI."""

    _SLI_NAME = "thoth_integrations"

    sli_columns = [
        "integration",
        "periodic",
        "total"
    ]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration

    def _aggregate_info(self):
        """Aggregate info required for Thoth Integrations SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._create_inputs_for_df_sli,
        }

    def _query_sli(self) -> List[str]:
        """Aggregate queries for Thoth Integrations SLI Report."""
        queries = {}
        for thoth_integration in self.configuration.thoth_integrations:
            result = self._aggregate_queries(thoth_integration=thoth_integration)

            for query_name, query in result.items():
                queries[query_name] = query

        return queries

    def _aggregate_queries(self, thoth_integration: str):
        """Aggregate Thoth integrations queries."""
        query_labels_integrations = (
            f'{{instance="{self.configuration.instance}", thoth_integration="{thoth_integration}"}}'
        )

        return {
            f"{thoth_integration}_counts_use": {
                "query": f"thoth_graphdb_adviser_count_per_source_type{query_labels_integrations}",
                "requires_range": True,
                "type": "delta",
            },
            f"{thoth_integration}_counts_total": {
                "query": f"thoth_graphdb_adviser_count_per_source_type{query_labels_integrations}",
                "requires_range": True,
                "type": "latest",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate SLI for report for Thoth Integrations SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for thoth_integration in self.configuration.thoth_integrations:
            name = thoth_integration.lower()
            html_inputs[name] = {}

            thoth_integration_counts_use = sli[f"{thoth_integration}_counts_use"]
            thoth_integration_counts_total = sli[f"{thoth_integration}_counts_total"]

            if thoth_integration_counts_use != "ErrorMetricRetrieval":
                html_inputs[name]["periodic"] = thoth_integration_counts_use
            else:
                html_inputs[name]["periodic"] = np.nan

            if thoth_integration_counts_total != "ErrorMetricRetrieval":
                html_inputs[name]["total"] = thoth_integration_counts_total
            else:
                html_inputs[name]["total"] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Thoth Integrations SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)
        report = HTMLTemplates.thoth_integrations_template(html_inputs=html_inputs)

        return report

    def _create_inputs_for_df_sli(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> Dict[str, Any]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        df_inputs = []

        for thoth_integration in self.configuration.thoth_integrations:
            name = thoth_integration.lower()
            df_input = {}

            thoth_integration_counts_use = sli[f"{thoth_integration}_counts_use"]
            thoth_integration_counts_total = sli[f"{thoth_integration}_counts_total"]

            if thoth_integration_counts_use != "ErrorMetricRetrieval":
                periodic = thoth_integration_counts_use
            else:
                periodic = np.nan

            if thoth_integration_counts_total != "ErrorMetricRetrieval":
                total = thoth_integration_counts_total
            else:
                total = np.nan

            df_inputs.append(
                {
                    "datetime": datetime,
                    "timestamp": timestamp,
                    "integration": name,
                    "periodic": periodic,
                    "total": total,
                },
            )

        return df_inputs
