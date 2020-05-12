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

"""This file contains class for Solved Python Packages SLI."""

import logging
import os
import datetime

from typing import Dict, List, Any

from .sli_base import SLIBase


_INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]
_INTERVAL = "7d"
_LOGGER = logging.getLogger(__name__)


class SLISolvedPythonPackages(SLIBase):
    """This class contain functions for Solved Python Packages SLI."""

    _SLI_NAME = "solved_python_packages"

    def _aggregate_info(self):
        """"Aggregate info required for solved_python_packages SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for solved_python_packages SLI Report."""
        query_labels = f'{{instance="{_INSTANCE}", main_table="python_package_version"}}'
        return {
            "learned_packages": f"thoth_graphdb_total_main_records{query_labels}"
            + f" - min_over_time(thoth_graphdb_total_main_records{query_labels}[{_INTERVAL}])"
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for solved_python_packages SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        report = f"<br><br> \
                    Thoth solved <strong>{int(sli['learned_packages'])} Python Packages </strong> in the last week. \
                    <br>"
        return report
