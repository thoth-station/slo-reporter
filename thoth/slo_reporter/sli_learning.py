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

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_INSTANCE = "dry_run"

if not Configuration.DRY_RUN:
    _INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]

_LOGGER = logging.getLogger(__name__)

_REGISTERED_LEARNING_MEASUREMENT_UNIT = {
    "max_learning_rate": {"name": "Learning Rate", "measurement_unit": "packages/hour"},
    "learned_packages": {"name": "Knowledge increase", "measurement_unit": "packages"},
    "solvers": {"name": "Number of Solvers", "measurement_unit": ""},
    "new_solvers": {"name": "New Solvers", "measurement_unit": ""},
}


class SLILearning(SLIBase):
    """This class contains functions for Learning Rate SLI."""

    _SLI_NAME = "learning_rate"

    def _aggregate_info(self):
        """Aggregate info required for learning quantities SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for learning quantities SLI Report."""
        query_labels = f'{{instance="{_INSTANCE}", job="Thoth Metrics ({Configuration._ENVIRONMENT})"}}'

        return {
            "max_learning_rate": f"max_over_time(\
                increase(\
                    thoth_graphdb_unsolved_python_package_versions_change_total{query_labels}[1h]\
                        )[{Configuration._INTERVAL}:1h])",
            "learned_packages": f"sum(delta(\
                thoth_graphdb_total_number_solved_python_packages{query_labels}[{Configuration._INTERVAL}]))",
            "solvers": f"thoth_graphdb_total_number_solvers{query_labels}",
            "new_solvers": f"delta(thoth_graphdb_total_number_solvers{query_labels}[{Configuration._INTERVAL}])",
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for learning quantities SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        for learning_quantity in _REGISTERED_LEARNING_MEASUREMENT_UNIT.keys():
            if sli[learning_quantity] or sli[learning_quantity] == 0:
                value = int(sli[learning_quantity])
            else:
                value = "Nan"

            html_inputs.append(
                [
                    _REGISTERED_LEARNING_MEASUREMENT_UNIT[learning_quantity]["name"],
                    value,
                    _REGISTERED_LEARNING_MEASUREMENT_UNIT[learning_quantity]["measurement_unit"],
                ],
            )

        report = HTMLTemplates.thoth_learning_template(html_inputs=html_inputs)
        return report
