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

"""This file contains class for Thoth User-API."""

import logging
import os
import datetime

from typing import Dict, List, Any

from .sli_base import SLIBase
from .sli_template import HTMLTemplates
from .configuration import Configuration

_INSTANCE = "dry_run"

if not Configuration.DRY_RUN:
    _INSTANCE = os.environ["PROMETHEUS_INSTANCE_USER_API"]

_LOGGER = logging.getLogger(__name__)

_USER_API_MEASUREMENT_UNIT = {
    "avg_successfull_request": {"name": "Successfull requests User-API (avg)", "measurement_unit": "%"},
    "avg_up_time": {"name": "Uptime User-API (avg)", "measurement_unit": "%"},
}


class SLIUserAPI(SLIBase):
    """This class contains functions for User-API SLI."""

    _SLI_NAME = "user_api"

    def _aggregate_info(self):
        """Aggregate info required for User-API SLI Report."""
        return {"query": self._query_sli(), "report_method": self._report_sli}

    def _query_sli(self) -> List[str]:
        """Aggregate queries for User-API SLI Report."""
        query_labels = f'{{instance="{_INSTANCE}"}}'
        query_labels_get_total = f'{{instance="{_INSTANCE}", status="200"}}'
        query_labels_post_total = f'{{instance="{_INSTANCE}", status="202"}}'
        query_labels_up = f'{{instance="{_INSTANCE}", job="Thoth User API Metrics ({Configuration._ENVIRONMENT})"}}'

        return {
            "avg_successfull_request": f"sum(\
                (avg(flask_http_request_total{query_labels_get_total}) + \
                avg(flask_http_request_total{query_labels_post_total})) / \
                sum(flask_http_request_total{query_labels}))",
            "avg_up_time": f"avg_over_time(up{query_labels_up}[{Configuration.INTERVAL}])",
        }

    def _report_sli(self, sli: Dict[str, Any]) -> str:
        """Create report for User-API SLI.

        @param sli: It's a dict of SLI associated with the SLI type.
        """
        html_inputs = []
        for user_api_quantity in _USER_API_MEASUREMENT_UNIT.keys():
            if sli[user_api_quantity] != "ErrorMetricRetrieval":
                value = abs(round(sli[user_api_quantity] * 100, 3))
            else:
                value = "Nan"

            html_inputs.append(
                [
                    _USER_API_MEASUREMENT_UNIT[user_api_quantity]["name"],
                    value,
                    _USER_API_MEASUREMENT_UNIT[user_api_quantity]["measurement_unit"],
                ]
            )
        report = HTMLTemplates.thoth_user_api_template(html_inputs=html_inputs)
        return report
