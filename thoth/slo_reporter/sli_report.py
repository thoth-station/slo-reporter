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

"""This file contains all sli metrics that should be included in the report."""

import logging

from .configuration import Configuration

from .sli_references import _add_dashbords

from thoth.slo_reporter.sli_learning import SLILearning
from thoth.slo_reporter.sli_thoth_services import SLIKebechet
from thoth.slo_reporter.sli_knowledge_graph import SLIKnowledgeGraph
from thoth.slo_reporter.sli_python_knowledge_graph import SLIPyPIKnowledgeGraph
from thoth.slo_reporter.sli_thoth_adviser_inputs import SLIThothIntegrations
from thoth.slo_reporter.sli_thoth_adviser_inputs import SLIThothRecommendationsTypesInputs
from thoth.slo_reporter.sli_thoth_adviser_inputs import SLIThothSolversInputs
from thoth.slo_reporter.sli_thoth_adviser_inputs import SLIThothBaseImagesInputs
from thoth.slo_reporter.sli_thoth_adviser_inputs import SLIThothHardwareInputs
from thoth.slo_reporter.sli_thoth_adviser_inputs import SLIThothIntegrationsUsers
from thoth.slo_reporter.sli_thoth_adviser_outputs import SLIThothAdviserReportsStatistics
from thoth.slo_reporter.sli_thoth_adviser_outputs import SLIThothAdviserJustificationsErrors
from thoth.slo_reporter.sli_apis import SLIUserAPI
from thoth.slo_reporter.sli_backends import SLIWorkflowQuality
from thoth.slo_reporter.sli_backends import SLIWorkflowTaskQuality
from thoth.slo_reporter.sli_backends import SLIWorkflowLatency
from thoth.slo_reporter.sli_backends import SLIWorkflowTaskLatency

from .sli_template import HTMLTemplates


_LOGGER = logging.getLogger(__name__)

SLI_CLASSES = [
    SLIPyPIKnowledgeGraph,
    SLIKnowledgeGraph,
    SLILearning,
    SLIThothIntegrationsUsers,
    SLIKebechet,
    SLIUserAPI,
    SLIThothIntegrations,
    SLIThothRecommendationsTypesInputs,
    SLIThothSolversInputs,
    SLIThothBaseImagesInputs,
    SLIThothHardwareInputs,
    SLIThothAdviserReportsStatistics,
    SLIThothAdviserJustificationsErrors,
    SLIWorkflowQuality,
    SLIWorkflowTaskQuality,
    SLIWorkflowLatency,
    SLIWorkflowTaskLatency,
]


class SLIReport:
    """This class contains all sections included in a report."""

    def __init__(self, configuration: Configuration):
        """Initialize SLI Report."""
        self.configuration = configuration

        self.report_subject = (
            f"Thoth Service Level Indicators Update Day" +
            f" ({self.configuration.end_time.strftime('%Y-%m-%d')}) ({self.configuration.environment} environment)"
        )
        _LOGGER.info(self.report_subject)

        self.report_start = HTMLTemplates.thoth_report_start_template()

        self.report_intro = HTMLTemplates.thoth_report_intro_template(
            html_inputs={
                "environment": self.configuration.environment,
                "end_time": str(self.configuration.end_time.strftime("%Y-%m-%d")),
            },
        )

        self.report_style = HTMLTemplates.thoth_report_style_template()

        self.report_sli_context = {}

        self.report_sli_context_columns = {}

        for sli_context in SLI_CLASSES:

            self.report_sli_context[sli_context._SLI_NAME] = sli_context(
                configuration=self.configuration,
            )._aggregate_info()

            self.report_sli_context_columns[sli_context._SLI_NAME] = sli_context(
                configuration=self.configuration,
            ).store_columns

        self.report_references = _add_dashbords(configuration=configuration)

        self.report_end = HTMLTemplates.thoth_report_end_template()
