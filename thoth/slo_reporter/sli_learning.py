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

"""This file contains class for Learning Quantities about Thoth."""

import logging
import os

import numpy as np

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_LOGGER = logging.getLogger(__name__)

_REGISTERED_LEARNING_MEASUREMENT_UNIT = {
    "average_learning_rate": {"name": "Learning Rate", "measurement_unit": "packages/hour"},
    "learned_packages": {"name": "Knowledge increase", "measurement_unit": "packages"},
    "solvers": {"name": "Number of Solvers", "measurement_unit": ""},
    "new_solvers": {"name": "New Solvers", "measurement_unit": ""},
}

_LEARNING_RATE_INTERVAL = "2h"


class SLILearning(SLIBase):
    """This class contains functions for Learning Rate SLI."""

    _SLI_NAME = "learning"

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration

    def _aggregate_info(self):
        """Aggregate info required for learning quantities SLI Report."""
        return {"query": self._query_sli(), "evaluation_method": self._evaluate_sli, "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for learning quantities SLI Report."""
        query_labels = f'{{instance="{self.configuration.instance}", job="Thoth Metrics ({self.configuration.environment})"}}'

        return {
            "average_learning_rate": {
                "query": f"increase(\
                    thoth_graphdb_unsolved_python_package_versions_change_total{query_labels}[{_LEARNING_RATE_INTERVAL}]\
                        )",
                "requires_range": True,
                "type": "average",
            },
            "learned_packages": {
                "query": f"sum(thoth_graphdb_total_number_solved_python_packages{query_labels})",
                "requires_range": True,
                "type": "min_max_only_ascending",
            },
            "solvers": {
                "query": f"thoth_graphdb_total_number_solvers{query_labels}",
                "requires_range": True,
                "type": "latest",
            },
            "new_solvers": {
                "query": f"thoth_graphdb_total_number_solvers{query_labels}",
                "requires_range": True,
                "type": "delta",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for learning quantities SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = {}

        for learning_quantity in _REGISTERED_LEARNING_MEASUREMENT_UNIT.keys():

            learning_quantity_data = _REGISTERED_LEARNING_MEASUREMENT_UNIT[learning_quantity]
            html_inputs[learning_quantity] = {}

            if sli[learning_quantity] != "ErrorMetricRetrieval":

                # if quntity uses delta
                if learning_quantity == "new_solvers":
                    html_inputs[learning_quantity]["value"] = int(sli[learning_quantity])
                else:
                    html_inputs[learning_quantity]["value"] = abs(int(sli[learning_quantity]))
            else:
                html_inputs[learning_quantity]["value"] = np.nan

            html_inputs[learning_quantity]["name"] = learning_quantity_data["name"]
            html_inputs[learning_quantity]["measurement_unit"] = learning_quantity_data["measurement_unit"]

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for learning quantities SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        report = HTMLTemplates.thoth_learning_template(html_inputs=html_inputs)
        return report
