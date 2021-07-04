#!/usr/bin/env python3
# slo-reporter
# Copyright(C) 2020 Sai Sankar Gochhayat
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

"""This file contains class for Kebechet."""

import logging
import datetime

import numpy as np

from typing import Dict, Any

from thoth.slo_reporter.sli_base import SLIBase
from thoth.slo_reporter.sli_template import HTMLTemplates
from thoth.slo_reporter.configuration import Configuration
from thoth.slo_reporter.utils import process_html_inputs

_LOGGER = logging.getLogger(__name__)

_REGISTERED_KEBECHET_QUANTITY = {
    "total_active_repositories": "Total active repositories",
}


class SLIKebechet(SLIBase):
    """This class contain functions for Kebechet SLI."""

    _SLI_NAME = "kebechet"

    sli_columns = [c for c in _REGISTERED_KEBECHET_QUANTITY]

    def __init__(self, configuration: Configuration):
        """Initialize SLI class."""
        self.configuration = configuration
        self.total_columns = self.default_columns + self.sli_columns
        self.store_columns = self.total_columns + ["delta_total_active_repositories"]

    def _query_sli(self) -> Dict[str, Any]:
        """Aggregate queries for Kebechet SLI Report."""
        query_labels = f'{{instance="{self.configuration.instance}", job="Thoth Metrics"}}'
        return {
            "total_active_repositories": {
                "query": f"thoth_kebechet_total_active_repo_count{query_labels}",
                "requires_range": True,
                "type": "latest",
            },
        }

    def _evaluate_sli(self, sli: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate SLI for report for Kebechet SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs: Dict[str, Any] = {}

        for knowledge_quantity in _REGISTERED_KEBECHET_QUANTITY.keys():
            html_inputs[knowledge_quantity] = {}
            html_inputs[knowledge_quantity]["name"] = _REGISTERED_KEBECHET_QUANTITY[knowledge_quantity]

            if sli[knowledge_quantity] != "ErrorMetricRetrieval":
                html_inputs[knowledge_quantity]["value"] = int(sli[knowledge_quantity])
            else:
                html_inputs[knowledge_quantity]["value"] = np.nan

        return html_inputs

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Kebechet SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = self._evaluate_sli(sli=sli)

        if not self.configuration.dry_run:
            report = HTMLTemplates.thoth_kebechet_template(
                html_inputs=process_html_inputs(
                    html_inputs=html_inputs,
                    sli_name=self._SLI_NAME,
                    last_period_time=self.configuration.last_week_time,
                    ceph_sli=self.configuration.ceph_sli,
                    sli_columns=self.sli_columns,
                    store_columns=self.store_columns,
                ),
            )
        else:
            report = HTMLTemplates.thoth_kebechet_template(html_inputs=html_inputs)

        return report

    def _process_results_to_be_stored(
        self,
        sli: Dict[str, Any],
        datetime: datetime.datetime,
        timestamp: datetime.datetime,
    ) -> Dict[str, Any]:
        """Create inputs for SLI dataframe to be stored.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        parameters = locals()
        parameters.pop("self")

        output = self._create_default_inputs_for_df_sli(**parameters)

        html_inputs = self._evaluate_sli(sli=sli)

        output["delta_total_active_repositories"] = np.nan

        if not self.configuration.dry_run:
            html_inputs = process_html_inputs(
                html_inputs=html_inputs,
                sli_name=self._SLI_NAME,
                last_period_time=self.configuration.last_week_time,
                ceph_sli=self.configuration.ceph_sli,
                sli_columns=self.sli_columns,
                store_columns=self.store_columns,
                is_storing=True,
            )
            output["delta_total_active_repositories"] = html_inputs["total_active_repositories"]["change"]  # type: ignore

        return output
