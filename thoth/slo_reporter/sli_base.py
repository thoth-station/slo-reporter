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

import datetime

from typing import Dict, List, Any


class SLIBase:
    """This class contain base functions that need to be created for SLI."""

    _SLI_NAME = None

    default_columns = ["datetime", "timestamp"]
    sli_columns = []

    def _aggregate_info(self):
        """Aggregate info required for specific SLI Report."""
        return {
            "query": self._query_sli(),
            "evaluation_method": self._evaluate_sli,
            "report_method": self._report_sli,
            "df_method": self._process_results_to_be_stored,
        }

    def _query_sli(self) -> Dict[str, str]:
        """Aggregate queries for specific SLI Report."""
        raise NotImplementedError

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate SLI for report for specific SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        raise NotImplementedError

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for specific SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        raise NotImplementedError

    def _process_results_to_be_stored(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> Dict[str, Any]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        raise NotImplementedError

    def _create_default_inputs_for_df_sli(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> Dict[str, Any]:
        """Create default inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        df_inputs = {}
        df_inputs["datetime"] = datetime
        df_inputs["timestamp"] = timestamp

        sli_results = self._evaluate_sli(sli=sli)

        for metric in sli_results:

            if "value" in sli_results[metric]:
                df_inputs[metric] = sli_results[metric]["value"]

        return df_inputs
