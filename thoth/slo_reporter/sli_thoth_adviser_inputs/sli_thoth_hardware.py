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

"""This file contains class for Thoth Hardware SLI."""

import logging
import datetime

from typing import Dict, List, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration
from thoth.slo_reporter.utils import retrieve_thoth_sli_from_ceph

_LOGGER = logging.getLogger(__name__)


class SLIThothHardwareInputs(SLIBase):
    """This class contain functions for Thoth Hardware SLI."""

    _SLI_NAME = "adviser_hardware_info"

    sli_columns = [
        "cpu_model",
        "cpu_family",
        "total",
    ]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns

    def _query_sli(self) -> Dict[str, Any]:
        """Aggregate queries for Thoth Hardware SLI Report."""
        # advise-reporter computes these data daily.
        return {}

    def _evaluate_sli(self) -> Dict[str, Any]:
        """Evaluate SLI for report for Thoth Hardware SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs: Dict[str, Any] = {}
        total_quantity: Dict[str, Any] = {}

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
                daily_quantity_df = retrieve_thoth_sli_from_ceph(
                    self.configuration.ceph_sli,
                    sli_path,
                    [c for c in self.total_columns if c != "timestamp"],
                )

                for cpu_model in daily_quantity_df["cpu_model"].unique():
                    subset_df = daily_quantity_df[daily_quantity_df["cpu_model"] == cpu_model]

                    hardware = f"{subset_df['cpu_model'].values[0]}-{subset_df['cpu_family'].values[0]}"
                    if hardware not in total_quantity:
                        total_quantity[hardware] = {
                            "cpu_model": subset_df['cpu_model'].values[0],
                            "cpu_family": subset_df['cpu_family'].values[0],
                            "counts": subset_df["total"].values[0],
                        }
                    else:
                        total_quantity[hardware]["counts"] += subset_df["total"].values[0]

                current_initial_date += delta

            total_ = 0
            for _, total_counts in total_quantity.items():
                total_ += total_counts["counts"]

            for hardware_, hardware_info in total_quantity.items():
                html_inputs[hardware_] = {}

                html_inputs[hardware_]["cpu_model"] = hardware_info["cpu_model"]
                html_inputs[hardware_]["cpu_family"] = hardware_info["cpu_family"]

                if not hardware_info["counts"]:
                    html_inputs[hardware_]["new"] = 0
                    html_inputs[hardware_]["percentage"] = 0
                else:
                    percentage = hardware_info["counts"] / total_
                    html_inputs[hardware_]["new"] = "+" + "{}".format(int(hardware_info["counts"]))
                    html_inputs[hardware_]["percentage"] = abs(round(percentage * 100, 3))

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Thoth Hardware SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli()
        report = HTMLTemplates.thoth_hardware_template(html_inputs=html_inputs)

        return report

    def _process_results_to_be_stored(
        self, sli: Dict[str, Any], datetime: datetime.datetime, timestamp: datetime.datetime,
    ) -> List[Dict[str, Any]]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        return []
