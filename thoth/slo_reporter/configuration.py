#!/usr/bin/env python3
# thoth-slo-reporter
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

"""Configuration of SLO-reporter."""

import logging
import os
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)


class Configuration:
    """Configuration of SLO-reporter."""

    DRY_RUN = bool(int(os.getenv("DRY_RUN", 0)))

    if DRY_RUN:
        _ENVIRONMENT = "dry_run"

    if not DRY_RUN:
        _ENVIRONMENT = os.environ["THOTH_ENVIRONMENT"]

        _SERVER = os.environ["SMTP_SERVER"]
        _SENDER_ADDRESS = os.environ["SENDER_ADDRESS"]
        _ADDRESS_RECIPIENTS = os.environ["EMAIL_RECIPIENTS"]

        _PUSHGATEWAY_ENDPOINT = os.environ["PROMETHEUS_PUSHGATEWAY_URL"]

        _THANOS_URL = os.environ["THANOS_ENDPOINT"]
        _THANOS_TOKEN = os.environ["THANOS_ACCESS_TOKEN"]

        _BACKEND_NAMESPACE = os.environ["THOTH_BACKEND_NAMESPACE"]
        _MIDDLETIER_NAMESPACE = os.environ["THOTH_MIDDLETIER_NAMESPACE"]
        _AMUN_INSPECTION_NAMESPACE = os.environ["THOTH_AMUN_INSPECTION_NAMESPACE"]

    _INTERVAL = "7d"
