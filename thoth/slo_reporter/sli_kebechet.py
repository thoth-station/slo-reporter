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
import os

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_INSTANCE = "dry_run"

if not Configuration.DRY_RUN:
    _INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]

_LOGGER = logging.getLogger(__name__)


class SLIKebechet(SLIBase):
    """This class contain functions for Kebechet SLI."""

    _SLI_NAME = "kebechet"

    def _aggregate_info(self):
        """"Aggregate info required for Kebechet SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for Kebechet SLI Report."""
        query_labels = f'{{instance="{_INSTANCE}", job="Thoth Metrics ({Configuration._ENVIRONMENT})"}}'
        return {
            "Total active repositories": f"thoth_kebechet_total_active_repo_count{query_labels}",
            "Change in active repositories since last week": f"delta(\
                thoth_kebechet_total_active_repo_count{query_labels}[{Configuration._INTERVAL}])",
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for Kebechet SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        for knowledge_quantity in sli.keys():
            if sli[knowledge_quantity] or int(sli[knowledge_quantity]) == 0:
                value = abs(int(sli[knowledge_quantity]))
            else:
                value = "Nan"

            html_inputs.append([knowledge_quantity, value])
        report = HTMLTemplates.thoth_kebechet_template(html_inputs=html_inputs)
        return report
