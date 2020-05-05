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

"""This file contains all sli metrics that should be included in the report."""

import datetime
import logging

from sli_report import _metrics_python_packages


_END_TIME = datetime.datetime.now()
_START_TIME = _END_TIME - datetime.timedelta(days=7)
_START_TIME_EPOCH = int(_START_TIME.timestamp() * 1000)
_END_TIME_EPOCH = int(_END_TIME.timestamp() * 1000)

_LOGGER = logging.getLogger(__name__)


class SliMetricReport:
    """Metrics to be included in the report."""

    INITIAL_REPORT = (
        f"<strong>Thoth SLI Metrics from {_START_TIME.strftime('%Y-%m-%d')} to {_END_TIME.strftime('%Y-%m-%d')}.</strong>"
    )
    SOLVED_PYTHON_PACKAGES_REPORT = _metrics_python_packages(_START_TIME_EPOCH, _END_TIME_EPOCH)
