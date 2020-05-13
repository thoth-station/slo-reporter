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
import datetime

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates


_INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]
_ENVIRONMENT = os.environ["THOTH_ENVIRONMENT"]
_INTERVAL = "7d"
_LOGGER = logging.getLogger(__name__)

_REGISTERED_LEARNING_MEASUREMENT_UNIT = {
    "max_learning_rate": "packages/hour",
    "learned_packages": "-"
}


class SLILearning(SLIBase):
    """This class contain functions for Learning Rate SLI."""

    _SLI_NAME = "learning_rate"

    def _aggregate_info(self):
        """"Aggregate info required for learning_rate SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for learning_rate SLI Report."""
        query_labels = f'{{instance="{_INSTANCE}", job="Thoth Metrics ({_ENVIRONMENT})"}}'

        return {
            "max_learning_rate": f"max_over_time(\
                increase(\
                    thoth_graphdb_unsolved_python_package_versions_change_total{query_labels}[1h])[{_INTERVAL}:1h])",
            "learned_packages": f"sum(delta(thoth_graphdb_total_number_solved_python_packages{query_labels}[{_INTERVAL}]))"
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for learning_rate SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        for learning_quantity in _REGISTERED_LEARNING_MEASUREMENT_UNIT.keys():
            html_inputs.append(
                [
                    learning_quantity,
                    int(sli[learning_quantity]),
                    _REGISTERED_LEARNING_MEASUREMENT_UNIT[learning_quantity]
                ]
            )
        report = HTMLTemplates.thoth_learning_template(html_inputs=html_inputs)
        return report
