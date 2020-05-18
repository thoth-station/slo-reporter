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

"""This file contains all templates used to create the final html report."""

from pathlib import Path
from typing import List, Any, Dict
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

_FILE_LOADER = FileSystemLoader(Path.cwd().joinpath("thoth", "slo_reporter", "templates"))
ENV = Environment(loader=_FILE_LOADER)


class HTMLTemplates:
    """This class collects all HTML template used for the SLI report."""

    def thoth_report_style_template():
        """Create HTML template for the style."""
        template = ENV.get_template("style.html")
        return template.render()

    def thoth_pypi_knowledge_template(html_inputs: List[Any]):
        """Create HTML template to be used for PyPI knowledge graph info."""
        parameters = locals()
        template = ENV.get_template("thoth_knowledge_graph.html")
        return template.render(**parameters)

    def thoth_knowledge_template(html_inputs: List[Any]):
        """Create HTML template to be used for Thoth knowledge graph info."""
        parameters = locals()
        template = ENV.get_template("thoth_knowledge_graph.html")
        return template.render(**parameters)

    def thoth_learning_template(html_inputs: List[Any]):
        """Create HTML template to be used for Thoth learning info."""
        parameters = locals()
        template = ENV.get_template("thoth_learning.html")
        return template.render(**parameters)

    def thoth_user_api_template(html_inputs: List[Any]):
        """Create HTML template to be used for Thoth User-API info."""
        parameters = locals()
        template = ENV.get_template("thoth_user_api.html")
        return template.render(**parameters)

    def thoth_services_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth services."""
        parameters = locals()
        template = ENV.get_template("thoth_service.html")
        return template.render(**parameters)

    def thoth_references_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth references."""
        parameters = locals()
        template = ENV.get_template("thoth_references.html")
        return template.render(**parameters)
