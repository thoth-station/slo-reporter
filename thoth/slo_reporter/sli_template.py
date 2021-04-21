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
from jinja2 import Environment, FileSystemLoader

_FILE_LOADER = FileSystemLoader(Path.cwd().joinpath("thoth", "slo_reporter", "static"))
ENV = Environment(loader=_FILE_LOADER)


class HTMLTemplates:
    """This class collects all HTML template used for the SLI report."""

    @staticmethod
    def thoth_report_start_template():
        """Create HTML template for intro."""
        template = ENV.get_template("templates/start.html")
        return template.render()

    @staticmethod
    def thoth_report_intro_template(html_inputs: Dict[str, Any]):
        """Create HTML template for intro."""
        parameters = locals()
        template = ENV.get_template("templates/intro.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_report_style_template():
        """Create HTML template for the style."""
        template = ENV.get_template("templates/style.html")
        return template.render()

    @staticmethod
    def thoth_pypi_knowledge_template(html_inputs: List[Any]):
        """Create HTML template to be used for PyPI knowledge graph info."""
        parameters = locals()
        template = ENV.get_template("templates/pypi_knowledge_graph.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_knowledge_template(html_inputs: List[Any]):
        """Create HTML template to be used for Thoth knowledge graph info."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_knowledge_graph.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_learning_template(html_inputs: List[Any]):
        """Create HTML template to be used for Thoth learning info."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_learning.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_user_api_template(html_inputs: List[Any]):
        """Create HTML template to be used for Thoth User-API info."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_user_api.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_workflows_quality_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth services."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_workflow_quality.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_workflows_task_quality_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth services."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_workflow_task_quality.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_services_latency_template(html_inputs: Dict[str, Any], configuration_buckets: List[str]):
        """Create HTML template to be used for Thoth services."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_workflow_latency.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_workflows_task_latency_template(html_inputs: Dict[str, Any], configuration_buckets: List[str]):
        """Create HTML template to be used for Thoth services."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_workflow_task_latency.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_kebechet_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Kebechet."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_kebechet.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_integrations_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Integrations."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_integrations.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_integrations_users_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Integrations users."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_integrations_users.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_recommendations_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Recommendation."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_recommendations.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_solvers_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Adviser Solver inputs."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_solvers.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_base_image_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Adviser Base Image inputs."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_base_images.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_hardware_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Adviser Hardware inputs."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_hardware.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_reports_statistics_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Adviser statistics."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_adviser_statistics.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_justifications_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth Adviser justifications."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_adviser_justifications.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_references_template(html_inputs: Dict[str, Any]):
        """Create HTML template to be used for Thoth references."""
        parameters = locals()
        template = ENV.get_template("templates/thoth_references.html")
        return template.render(**parameters)

    @staticmethod
    def thoth_report_end_template():
        """Create HTML template for end."""
        template = ENV.get_template("templates/end.html")
        return template.render()
