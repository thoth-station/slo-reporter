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


"""This is a SLO Reporter for Thoth."""

from thoth.storages import __version__ as __storages__version__
from thoth.common import __version__ as __common__version__


__version__ = "0.18.0"
__service_version__ = f"{__version__}+\
    storages.{__storages__version__}+\
    common.{__common__version__}"
