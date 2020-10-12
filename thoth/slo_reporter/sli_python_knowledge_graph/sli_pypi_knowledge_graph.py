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

"""This file contains class for PyPI Knowledge Graph."""

import logging
import os
import datetime

import numpy as np

from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration


_LOGGER = logging.getLogger(__name__)

_REGISTERED_KNOWLEDGE_QUANTITY = {
    "total_packages": "Python Packages",
    "new_packages": "New Python Packages",
    "total_releases": "Python Packages Releases",
    "new_packages_releases": "New Python Packages Releases",
}


class SLIPyPIKnowledgeGraph(SLIBase):
    """This class contain functions for PyPI Knowledge Graph SLI."""

    _SLI_NAME = "pypi_knowledge_graph"

    sli_columns = [c for c in _REGISTERED_KNOWLEDGE_QUANTITY]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns

    def _aggregate_info(self):
        """Aggregate info required for knowledge graph SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._create_inputs_for_df_sli,
        }

    def _query_sli(self) -> List[str]:
        """Aggregate queries for knowledge graph SLI Report."""
        query_labels_packages = f'{{instance="{self.configuration.instance}", job="Thoth Metrics ({self.configuration.environment})", stats_type="packages"}}'
        query_labels_releases = f'{{instance="{self.configuration.instance}", job="Thoth Metrics ({self.configuration.environment})", stats_type="releases"}}'

        return {
            "total_packages": {
                "query": f"thoth_pypi_stats{query_labels_packages}",
                "requires_range": True,
                "type": "latest",
            },
            "new_packages": {
                "query": f"thoth_pypi_stats{query_labels_packages}",
                "requires_range": True,
                "type": "min_max",
            },
            "total_releases": {
                "query": f"thoth_pypi_stats{query_labels_releases}",
                "requires_range": True,
                "type": "latest",
            },
            "new_packages_releases": {
                "query": f"thoth_pypi_stats{query_labels_releases}",
                "requires_range": True,
                "type": "min_max",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for PyPI knowledge graph SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for knowledge_quantity in _REGISTERED_KNOWLEDGE_QUANTITY.keys():

            html_inputs[knowledge_quantity] = {}
            html_inputs[knowledge_quantity]["name"] = _REGISTERED_KNOWLEDGE_QUANTITY[knowledge_quantity]

            if sli[knowledge_quantity] != "ErrorMetricRetrieval":
                html_inputs[knowledge_quantity]["value"] = abs(int(sli[knowledge_quantity]))
            else:
                html_inputs[knowledge_quantity]["value"] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for PyPI knowledge graph SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        report = HTMLTemplates.thoth_pypi_knowledge_template(html_inputs=html_inputs)
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
