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

"""This is the main script of Thoth SLO reporter.

    Thanks to DataHub Team in the Red Hat AICoE!!
"""

import os
import logging
import smtplib
import datetime
import pandas as pd

from prometheus_api_client import Metric, MetricsList, PrometheusConnect
from prometheus_api_client.utils import parse_datetime, parse_timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


_LOGGER = logging.getLogger("thoth.slo_reporter")


def push_thoth_sli_weekly_metric(weekly_value_metric, prometheus_registry, pushgateway_endpoint):
    """Push Thoth SLI weekly metric to PushGateway."""
    weekly_metric = Gauge("thoth_sli_weekly", "Weekly Thoth Service Level Indicators", registry=prometheus_registry)

    weekly_value_metric = float(weekly_value_metric[0]["value"][1])
    weekly_metric.set(weekly_value_metric)

    push_to_gateway(pushgateway_endpoint, job="Weekly Thoth SLI", registry=prometheus_registry)

    return weekly_value_metric


def generate_services_table_html(prometheus_connect_object):
    """Generate Thoth Service Level Indicators table in HTML."""
    thoth_sli = []

    thoth_sli_df = pd.DataFrame(thoth_sli)
    return thoth_sli_df.to_html()


def send_sli_email(server, sender_address, recipients, learned_packages, service_availabilities):
    """Send email about Thoth Service Level Objectives."""
    _MAIL_SERVER = smtplib.SMTP(server)

    msg = MIMEMultipart()
    msg["Subject"] = "Thoth Weekly Service Level Indicators"
    msg["From"] = sender_address
    msg["To"] = recipients

    email_message = generate_email(int(learned_packages))

    msg.attach(email_message)

    _MAIL_SERVER.sendmail(sender_address, recipients, msg.as_string())


def generate_email(learned_packages: int):
    """General email to be sent."""
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=7)
    start_time_epoch = int(start_time.timestamp() * 1000)
    end_time_epoch = int(end_time.timestamp() * 1000)

    grafana_dashboard_url = f"https://grafana.datahub.redhat.com/dashboard/db/thoth-knowledge-graph-content-metrics-stage?" + \
                            f"refresh=1m&panelId=23&fullscreen&orgId=1&from={start_time_epoch}&to={end_time_epoch}"

    return MIMEText(
        f"<strong>Thoth Solved {learned_packages} Python Packages in the last week.</strong> \
            <br><br> \
            Python Packages Information collected in the last week by Thoth. \
            <br> \
            The following dashboard panel contains Python Packages info collected: <a href='{grafana_dashboard_url}'> Python Packages Info.</a> \
            <br>",
        "html",
    )


def main():
    """Main function for Thoth Service Level Objectives (SLO) Reporter."""
    _SERVER = os.environ["SMTP_SERVER"]
    _SENDER_ADDRESS = os.environ["SENDER_ADDRESS"]
    _ADDRESS_RECIPIENTS = os.environ["EMAIL_RECIPIENTS"]

    _THANOS_URL = os.environ["THANOS_ENDPOINT"]
    _THANOS_TOKEN = os.environ["THANOS_ACCESS_TOKEN"]
    _PUSHGATEWAY_ENDPOINT = os.environ["PROMETHEUS_PUSHGATEWAY_URL"]

    prometheus_registry = CollectorRegistry()

    pc = PrometheusConnect(url=_THANOS_URL, headers={"Authorization": f"bearer {_THANOS_TOKEN}"}, disable_ssl=True)
    query = (
        'thoth_graphdb_total_main_records{instance="metrics-exporter-thoth-frontend-stage.cloud.paas.psi.redhat.com:80", main_table="python_package_version"}'
        + ' - min_over_time(thoth_graphdb_total_main_records{instance="metrics-exporter-thoth-frontend-stage.cloud.paas.psi.redhat.com:80", main_table="python_package_version"}[7d])'
    )
    learned_packages_weekly = pc.custom_query(query=query)

    weekly_sli_value = push_thoth_sli_weekly_metric(learned_packages_weekly, prometheus_registry, _PUSHGATEWAY_ENDPOINT)
    _LOGGER.info(f"Pushed Thoth weekly SLI to Prometheus Pushgateway.")
    thoth_sli_html = generate_services_table_html(pc)
    _LOGGER.info(f"Correctly generated Thoth weekly SLI HTML.")
    send_sli_email(_SERVER, _SENDER_ADDRESS, _ADDRESS_RECIPIENTS, weekly_sli_value, thoth_sli_html)
    _LOGGER.info(f"Thoth weekly SLI correctly sent.")


if __name__ == "__main__":
    main()
