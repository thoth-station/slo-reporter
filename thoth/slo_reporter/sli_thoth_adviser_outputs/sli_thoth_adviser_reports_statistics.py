#!/usr/bin/env python3
# slo-reporter
# Copyright(C) 2021 Francesco Murdaca
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
from thoth.slo_reporter.utils import retrieve_thoth_sli_from_ceph

_LOGGER = logging.getLogger(__name__)


class SLIThothAdviserReportsStatistics(SLIBase):
    """This class contain functions for Thoth Adviser Reports Statistics SLI."""

    _SLI_NAME = "adviser_statistics"

    sli_columns = [
        "adviser_version",
        "success",
        "failure"
    ]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns

    def _query_sli(self) -> List[str]:
        """Aggregate queries for Thoth Adviser Reports Statistics SLI Report."""
        # advise-reporter computes these data daily.
        return {}

    def _evaluate_sli(self) -> Dict[str, Any]:
        """Evaluate SLI for report for Thoth Adviser Reports Statistics SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        total_statistics: Dict[str, Any] = {}

        days = self.configuration.adviser_inputs_analysis_days
        delta = datetime.timedelta(days=1)

        if not self.configuration.dry_run:

            e_time = self.configuration.start_time.strftime('%Y-%m-%d').split("-")
            current_end_time = datetime.date(year=int(e_time[0]), month=int(e_time[1]), day=int(e_time[2])) + datetime.timedelta(days=1)
            current_initial_date = current_end_time  - datetime.timedelta(days=days)

            while current_initial_date < current_end_time:

                _LOGGER.info(f"Analyzing for start date: {current_initial_date}")

                sli_path = f"{self._SLI_NAME}/{self._SLI_NAME}-{current_initial_date}.csv"
                daily_statistics_df = retrieve_thoth_sli_from_ceph(
                    self.configuration.ceph_sli,
                    sli_path,
                    [c for c in self.total_columns if c not in ["timestamp", "datetime"]]
                )

                for adviser_version in daily_statistics_df["adviser_version"].unique():
                    subset_df = daily_statistics_df[daily_statistics_df["adviser_version"] == adviser_version]

                    s_counts = 0
                    f_counts = 0

                    if not subset_df.empty:
                        s_counts = subset_df[subset_df["adviser_version"] == adviser_version][
                            "success"
                        ].values[0]
                        f_counts = subset_df[subset_df["adviser_version"] == adviser_version][
                            "failure"
                        ].values[0]

                    if adviser_version not in total_statistics:
                        total_statistics[adviser_version] = {}

                        total_statistics[adviser_version]["success"] = s_counts
                        total_statistics[adviser_version]["failure"] = f_counts
                    else:
                        total_statistics[adviser_version]["success"] += s_counts
                        total_statistics[adviser_version]["failure"] += f_counts

                current_initial_date += delta

            for adviser_version, statistics_info in total_statistics.items():

                total = statistics_info["success"] + statistics_info["failure"]

                success_p = statistics_info["success"] / total
                failure_p = statistics_info["failure"] / total

                html_inputs.append(
                    {
                        "adviser_version": adviser_version,
                        "success_p": abs(round(success_p * 100, 3)),
                        "failure_p": abs(round(failure_p * 100, 3))
                    }
                )

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Thoth Adviser Reports Statistics SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli()
        report = HTMLTemplates.thoth_reports_statistics_template(html_inputs=html_inputs)

        return report

    def _process_results_to_be_stored(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> List[Dict[str, Any]]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        return []
