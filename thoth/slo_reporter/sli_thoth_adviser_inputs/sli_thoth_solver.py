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

"""This file contains class for Thoth Solvers SLI."""

import logging
import datetime

from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration
from thoth.slo_reporter.utils import evaluate_total_data_window_days

_LOGGER = logging.getLogger(__name__)


class SLIThothSolversInputs(SLIBase):
    """This class contain functions for Thoth Solvers SLI."""

    _SLI_NAME = "adviser_solver_info"

    sli_columns = [
        "solver",
        "total"
    ]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns

    def _query_sli(self) -> List[str]:
        """Aggregate queries for Thoth Solvers SLI Report."""
        # advise-reporter computes these data daily.
        return {}

    def _evaluate_sli(self) -> Dict[str, Any]:
        """Evaluate SLI for report for Thoth Solvers SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = evaluate_total_data_window_days(
            sli_name=self._SLI_NAME,
            total_columns=self.total_columns,
            quantity="solver",
            configuration=self.configuration
        )

        for solver in html_inputs:
            solver_parts = solver.split("-")
            html_inputs[solver]["os_name"] = solver_parts[0]
            html_inputs[solver]["os_version"] = solver_parts[1]
            html_inputs[solver]["python_version"] = ".".join([v for v in solver_parts[2].replace("py", "")])

        return html_inputs


    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Thoth Solvers SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli()
        report = HTMLTemplates.thoth_solvers_template(html_inputs=html_inputs)

        return report

    def _process_results_to_be_stored(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> List[Dict[str, Any]]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        return []
