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

"""This file contains class for Thoth Knowledge Graph."""

import logging
import os
import datetime

import numpy as np

from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration
from thoth.slo_reporter.utils import retrieve_thoth_sli_from_ceph

_LOGGER = logging.getLogger(__name__)

_REGISTERED_KNOWLEDGE_QUANTITY = {
    "python_indices_registered": "Python Indices",
    "total_packages": "Python Packages",
    "new_packages": "New Python Packages",
    "total_releases": "Python Packages Releases",
    "new_packages_releases": "New Python Packages Releases",
}


class SLIKnowledgeGraph(SLIBase):
    """This class contain functions for Knowledge Graph SLI."""

    _SLI_NAME = "knowledge_graph"

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
        query_labels = (
            f'{{instance="{self.configuration.instance}", job="Thoth Metrics"}}'
        )

        return {
            "python_indices_registered": {
                "query": f"thoth_graphdb_total_python_indexes{query_labels}",
                "requires_range": True,
                "type": "latest",
            },
            "total_packages": {
                "query": f"thoth_graphdb_sum_python_packages_per_indexes{query_labels}",
                "requires_range": True,
                "type": "latest",
            },
            "new_packages": {
                "query": f"thoth_graphdb_sum_python_packages_per_indexes{query_labels}",
                "requires_range": True,
                "type": "delta",
            },
            "total_releases": {
                "query": f"thoth_graphdb_number_python_package_versions{query_labels}",
                "requires_range": True,
                "type": "latest",
            },
            "new_packages_releases": {
                "query": f"thoth_graphdb_number_python_package_versions{query_labels}",
                "requires_range": True,
                "type": "delta",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for knowledge graph SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for knowledge_quantity in _REGISTERED_KNOWLEDGE_QUANTITY.keys():

            html_inputs[knowledge_quantity] = {}
            html_inputs[knowledge_quantity]["name"] = _REGISTERED_KNOWLEDGE_QUANTITY[knowledge_quantity]

            if sli[knowledge_quantity] != "ErrorMetricRetrieval":
                html_inputs[knowledge_quantity]["value"] = int(sli[knowledge_quantity])
            else:
                html_inputs[knowledge_quantity]["value"] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for knowledge graph SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        if not self.configuration.dry_run:
            sli_path = f"{self._SLI_NAME}/{self._SLI_NAME}-{self.configuration.last_week_time}.csv"
            last_week_data = retrieve_thoth_sli_from_ceph(self.configuration.ceph_sli, sli_path, self.total_columns)

            for c in ["new_packages", "new_packages_releases"]:
                html_inputs[c]["change"] = "N/A"

            for c in ["python_indices_registered", "total_packages", "total_releases"]:
                diff = (html_inputs[c]["value"] - last_week_data[c])[0].item()
                if diff > 0:
                    html_inputs[c]["change"] = "+{:.0f}".format(diff)
                elif diff < 0:
                    html_inputs[c]["change"] = "{:.0f}".format(diff)
                else:
                    html_inputs[c]["change"] = diff

        report = HTMLTemplates.thoth_knowledge_template(html_inputs=html_inputs)
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
