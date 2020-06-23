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

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_INSTANCE = "dry_run"

if not Configuration.DRY_RUN:
    _INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]

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

    def _aggregate_info(self):
        """Aggregate info required for knowledge graph SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for knowledge graph SLI Report."""
        query_labels = f'{{instance="{_INSTANCE}", job="Thoth Metrics ({Configuration._ENVIRONMENT})"}}'

        return {
            "python_indices_registered": f"thoth_graphdb_total_python_indexes{query_labels}",
            "total_packages": f"thoth_graphdb_sum_python_packages_per_indexes{query_labels}",
            "new_packages": f"delta(\
                thoth_graphdb_sum_python_packages_per_indexes{query_labels}[{Configuration.INTERVAL}])",
            "total_releases": f"thoth_graphdb_number_python_package_versions{query_labels}",
            "new_packages_releases": f"delta(\
                thoth_graphdb_number_python_package_versions{query_labels}[{Configuration.INTERVAL}])",
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for knowledge graph SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        for knowledge_quantity in _REGISTERED_KNOWLEDGE_QUANTITY.keys():
            if sli[knowledge_quantity] != "ErrorMetricRetrieval":
                value = abs(int(sli[knowledge_quantity]))
            else:
                value = "Nan"

            html_inputs.append([_REGISTERED_KNOWLEDGE_QUANTITY[knowledge_quantity], value])
        report = HTMLTemplates.thoth_knowledge_template(html_inputs=html_inputs)
        return report
