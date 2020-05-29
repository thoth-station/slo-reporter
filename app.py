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

"""This is the main script of Thoth SLO reporter."""

import os
import logging
import smtplib
import datetime
import base64
import webbrowser
import tempfile

from typing import Dict
from pathlib import Path

from prometheus_api_client import Metric, MetricsList, PrometheusConnect
from prometheus_api_client.utils import parse_datetime, parse_timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from thoth.slo_reporter.sli_report import SLIReport
from thoth.slo_reporter import __service_version__
from thoth.slo_reporter.configuration import Configuration


_LOGGER = logging.getLogger("thoth.slo_reporter")
_LOGGER.info(f"Thoth SLO Reporter v%s", __service_version__)

_DRY_RUN = Configuration.DRY_RUN

_DEBUG_LEVEL = bool(int(os.getenv("DEBUG_LEVEL", 0)))

if _DEBUG_LEVEL:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if not _DRY_RUN:
    _PROMETHEUS_REGISTRY = CollectorRegistry()
    _THOTH_WEEKLY_SLI = Gauge(
        f"thoth_sli_weekly_{Configuration._ENVIRONMENT}",
        "Weekly Thoth Service Level Indicators",
        ["sli_type", "metric_name"],
        registry=_PROMETHEUS_REGISTRY,
    )


def collect_metrics():
    """Collect metrics from Prometheus/Thanos."""
    if not _DRY_RUN:
        pc = PrometheusConnect(
            url=Configuration._THANOS_URL,
            headers={"Authorization": f"bearer {Configuration._THANOS_TOKEN}"},
            disable_ssl=True,
        )

    collected_info = {}
    for sli_name, sli_methods in SLIReport.REPORT_SLI_CONTEXT.items():
        _LOGGER.info(f"Retrieving data for... {sli_name}")
        collected_info[sli_name] = {}
        for query_name, query in sli_methods["query"].items():
            _LOGGER.info(f"Querying... {query_name}")
            try:
                if not _DRY_RUN:
                    metric_data = pc.custom_query(query=query)
                    _LOGGER.info(f"Metric obtained... {metric_data}")
                else:
                    metric_data = [{"metric": "dry run", "value": [datetime.datetime.utcnow(), 1]}]
                collected_info[sli_name][query_name] = float(metric_data[0]["value"][1])
            except Exception as e:
                _LOGGER.exception(f"Could not gather metric for {sli_name}-{query_name}...{e}")
                pass
                collected_info[sli_name][query_name] = None

    return collected_info


def push_thoth_sli_weekly_metrics(weekly_metrics: Dict[str, Metric]):
    """Push Thoth SLI weekly metric to PushGateway."""
    for sli_type, metric_data in weekly_metrics.items():
        for metric_name, weekly_value_metric in metric_data.items():
            if weekly_value_metric:
                _THOTH_WEEKLY_SLI.labels(sli_type=sli_type, metric_name=metric_name).set(weekly_value_metric)
                _LOGGER.info("(sli_type=%r, metric_name=%r)=%r", sli_type, metric_name, weekly_value_metric)

    push_to_gateway(Configuration._PUSHGATEWAY_ENDPOINT, job="Weekly Thoth SLI", registry=_PROMETHEUS_REGISTRY)
    _LOGGER.info(f"Pushed Thoth weekly SLI to Prometheus Pushgateway.")


def generate_email(sli_metrics: Dict[str, float]):
    """Generate email to be sent."""
    message = SLIReport.REPORT_START
    message += SLIReport.REPORT_STYLE
    message += SLIReport.REPORT_INTRO

    for sli_name, metric_data in sli_metrics.items():
        report_method = SLIReport.REPORT_SLI_CONTEXT[sli_name]["report_method"]
        message += "\n" + report_method(metric_data)

    message += SLIReport.REPORT_REFERENCES

    message += SLIReport.REPORT_END

    html_message = MIMEText(message, "html")
    _LOGGER.debug(f"Email message: {html_message}")

    html_file = open(Path.cwd().joinpath("thoth", "slo_reporter", "SLO-reporter.html"), "w")
    html_file.write(message)
    html_file.close()

    if _DRY_RUN:
        return message

    return html_message


def send_sli_email(email_message: MIMEText):
    """Send email about Thoth Service Level Objectives."""
    server = Configuration._SERVER
    sender_address = Configuration._SENDER_ADDRESS
    recipients = Configuration._ADDRESS_RECIPIENTS

    msg = MIMEMultipart()
    msg["Subject"] = SLIReport.REPORT_SUBJECT
    msg["From"] = sender_address
    msg["To"] = recipients

    msg.attach(email_message)
    _MAIL_SERVER = smtplib.SMTP(server)
    _MAIL_SERVER.sendmail(sender_address, recipients, msg.as_string())
    _LOGGER.info(f"Thoth weekly SLI correctly sent.")


def main():
    """Main function for Thoth Service Level Objectives (SLO) Reporter."""
    if _DRY_RUN:
        _LOGGER.info("Dry run...")
    weekly_sli_values_map = collect_metrics()

    if not _DRY_RUN:
        push_thoth_sli_weekly_metrics(weekly_sli_values_map)

    email_message = generate_email(weekly_sli_values_map)

    if _DRY_RUN:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
            url = "file://" + f.name
            f.write(email_message)
        webbrowser.open(url)

    if not _DRY_RUN:
        send_sli_email(email_message)


if __name__ == "__main__":
    main()
