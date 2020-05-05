#!/usr/bin/env python3
# slo-reporter
# Copyright(C) 2010 Red Hat, Inc.
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

"""This file contains all html report created for each sli metric."""

import datetime
import logging

from sli_report import _metrics_python_packages


_LOGGER = logging.getLogger(__name__)


class SliMetrics:
    """Metrics and dashboards to be included in the report."""

    END_TIME = datetime.datetime.now()
    START_TIME = END_TIME - datetime.timedelta(days=7)
    START_TIME_EPOCH = int(START_TIME.timestamp() * 1000)
    END_TIME_EPOCH = int(END_TIME.timestamp() * 1000)

    INITIAL_MESSAGE = (
        f"<strong>Thoth SLI Metrics from {START_TIME.strftime('%Y-%m-%d')} to {END_TIME.strftime('%Y-%m-%d')}.</strong>"
    )
    SOLVED_PYTHON_PACKAGES = _metrics_python_packages(START_TIME_EPOCH, END_TIME_EPOCH)
