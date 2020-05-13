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

"""This file contains references to be included in the final report."""

import os
import logging
import datetime

from .sli_template import HTMLTemplates

_ENVIRONMENT = os.environ["THOTH_ENVIRONMENT"]
_LOGGER = logging.getLogger(__name__)


def _add_dashbords(start_time_epoch: datetime.datetime, end_time_epoch: datetime.datetime):
    """Create dashboard link for report."""
    html_inputs = {}

    knowledge_graph_dashboard_name = f"thoth-knowledge-graph-content-metrics-{_ENVIRONMENT}"
    knowledge_graph_dashboard_url = (
        f"https://grafana.datahub.redhat.com/dashboard/db/{knowledge_graph_dashboard_name}?"
        + f"refresh=1m&orgId=1&from={start_time_epoch}&to={end_time_epoch}"
    )
    html_inputs["Thoth Knowledge Graph"] = knowledge_graph_dashboard_url

    sli_slo_dashboard_name = f"thoth-sli-slo"
    sli_slo_dashboard_url = (
        f"https://grafana.datahub.redhat.com/dashboard/db/{sli_slo_dashboard_name}?"
        + f"refresh=1m&orgId=1&from={start_time_epoch}&to={end_time_epoch}"
    )
    html_inputs["Thoth SLI/SLO"] = sli_slo_dashboard_url

    report = HTMLTemplates.thoth_references_template(html_inputs=html_inputs)
    return report
