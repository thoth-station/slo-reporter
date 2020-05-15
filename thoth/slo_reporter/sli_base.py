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

"""This file contains basic class for all SLI to be included in a report."""

from typing import Dict, List, Any


class SLIBase:
    """This class contain base functions that need to be created for SLI."""

    _SLI_NAME = None

    def _aggregate_info(self):
        """"Aggregate info required for specific SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> Dict[str, str]:
        """Aggregate queries for specific SLI Report."""
        raise NotImplementedError

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for specific SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        raise NotImplementedError
