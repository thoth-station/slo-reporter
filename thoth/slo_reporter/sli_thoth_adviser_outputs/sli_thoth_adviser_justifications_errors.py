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


class SLIThothAdviserJustificationsErrors(SLIBase):
    """This class contain functions for Thoth Adviser Justifications Errors SLI."""

    _SLI_NAME = "adviser_justifications"

    sli_columns = [
        "message",
        "total",
        "type",
        "adviser_version",
    ]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns

    def _query_sli(self) -> Dict[str, Any]:
        """Aggregate queries for Thoth Adviser Justifications Errors SLI Report."""
        # advise-reporter computes these data daily.
        return {}

    def _evaluate_sli(self) -> List[Dict[str, Any]]:
        """Evaluate SLI for report for Thoth Adviser Justifications Errors SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        total_justifications: Dict[str, Any] = {}

        days = self.configuration.adviser_inputs_analysis_days
        delta = datetime.timedelta(days=1)

        if not self.configuration.dry_run:

            e_time = self.configuration.start_time.strftime('%Y-%m-%d').split("-")
            current_end_time = datetime.date(
                year=int(e_time[0]), month=int(e_time[1]), day=int(e_time[2]),
            ) + datetime.timedelta(days=1)
            current_initial_date = current_end_time  - datetime.timedelta(days=days)

            while current_initial_date < current_end_time:

                _LOGGER.info(f"Analyzing for start date: {current_initial_date}")

                sli_path = f"{self._SLI_NAME}/{self._SLI_NAME}-{current_initial_date}.csv"
                daily_justifications_df = retrieve_thoth_sli_from_ceph(
                    self.configuration.ceph_sli,
                    sli_path,
                    [c for c in self.total_columns if c != "timestamp"],
                )

                for message in daily_justifications_df["message"].unique():
                    for adviser_version in daily_justifications_df["adviser_version"].unique():
                        subset_df = daily_justifications_df[
                            (daily_justifications_df["message"] == message) &
                            (daily_justifications_df["adviser_version"] == adviser_version)
                        ]

                        if subset_df.shape[0] < 1:
                            continue

                        counts = subset_df["total"].values[0]

                        message_type = subset_df["type"].values[0]

                        if message_type != "ERROR":
                            continue

                        if adviser_version not in total_justifications:
                            total_justifications[adviser_version] = {}

                            total_justifications[adviser_version][message] = counts
                        else:
                            if message not in total_justifications[adviser_version]:
                                total_justifications[adviser_version][message] = counts
                            else:
                                total_justifications[adviser_version][message] += counts

                current_initial_date += delta

            for adviser_version, justifications_info in total_justifications.items():

                total_errors = 0
                for _, errors_counts in justifications_info.items():
                    total_errors += errors_counts

                for justification, counts in justifications_info.items():

                    if not counts:
                        total = "0"
                        percentage = 0
                    else:
                        total = "+" + "{}".format(int(counts))
                        percentage = counts / total_errors

                    html_inputs.append(
                        {
                            "adviser_version": adviser_version,
                            "justification": justification,
                            "total": total,
                            "percentage": abs(round(percentage * 100, 3)),
                        },
                    )

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Thoth Adviser Justifications Errors SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli()
        report = HTMLTemplates.thoth_justifications_template(html_inputs=html_inputs)

        return report

    def _process_results_to_be_stored(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> List[Dict[str, Any]]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        return []
