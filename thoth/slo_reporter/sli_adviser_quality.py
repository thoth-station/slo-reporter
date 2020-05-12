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

"""This file contains class for Adviser Workflow Quality SLI."""

import logging
import os
import datetime

from typing import Dict, List, Any

from .sli_base import SLIBase


_INSTANCE = os.environ["PROMETHEUS_INSTANCE_METRICS_EXPORTER_FRONTEND"]
_INTERVAL = "7d"
_LOGGER = logging.getLogger(__name__)


class SLIAdviserQuality(SLIBase):
    """This class contain functions for Adviser Quality SLI."""

    _SLI_NAME = "adviser_quality"

    def _aggregate_info(self):
        """"Aggregate info required for adviser_quality SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for adviser_quality SLI Report."""
        query_labels_adviser_reports = f'{{instance="{_INSTANCE}", result_type="adviser"}}'
        query_labels_adviser_workflows_f = f'{{instance="{_INSTANCE}", label_selector="component=adviser", job="Thoth Metrics (stage)", workflow_status="Failed"}}'
        query_labels_adviser_workflows_e = f'{{instance="{_INSTANCE}", label_selector="component=adviser", job="Thoth Metrics (stage)", workflow_status="Error"}}'
        return {
            "adviser_reports": f"thoth_ceph_results_number{query_labels_adviser_reports}"
            + f" - min_over_time(thoth_ceph_results_number{query_labels_adviser_reports}[{_INTERVAL}])",
            "avg_adviser_workflows_failed": f"avg_over_time(thoth_workflows_status{query_labels_adviser_workflows_f}[{_INTERVAL}])",
            "avg_adviser_workflows_error": f"avg_over_time(thoth_workflows_status{query_labels_adviser_workflows_e}[{_INTERVAL}])",
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for adviser_quality SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        total_workflows = (
            int(sli["adviser_reports"])
            + int(sli["avg_adviser_workflows_failed"])
            + int(sli["avg_adviser_workflows_error"])
        )
        if total_workflows:
            successfull_percentage = (
                (
                    int(sli["adviser_reports"])
                    - int(sli["avg_adviser_workflows_failed"])
                    - int(sli["avg_adviser_workflows_error"])
                )
                / total_workflows
            ) * 100
            report = f"<br> \
                        Thoth Adviser was successfull <strong>{int(successfull_percentage)}% </strong> of the time in the last week. \
                        <br>"
        else:
            report = f"<br> \
                        Thoth Adviser did not run last week. \
                        <br>"
        return report
