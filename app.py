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
import ssl
import smtplib
import logging
import datetime
import webbrowser
import tempfile

import pandas as pd

from typing import Dict, Any
from pathlib import Path

from prometheus_api_client import Metric, PrometheusConnect
from prometheus_client import push_to_gateway

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from thoth.slo_reporter.sli_report import SLIReport
from thoth.slo_reporter import __service_version__
from thoth.slo_reporter.configuration import Configuration
from thoth.slo_reporter.utils import manipulate_retrieved_metrics_vector
from thoth.slo_reporter.utils import store_thoth_sli_on_ceph, connect_to_ceph


_LOGGER = logging.getLogger("thoth.slo_reporter")
_LOGGER.info("Thoth SLO Reporter v%s", __service_version__)

_DRY_RUN = bool(int(os.getenv("DRY_RUN", 0)))

INTERVAL_REPORT_DAYS = int(os.getenv("THOTH_INTERVAL_REPORT_NUMBER_DAYS", 1))
_LOGGER.info("Considering interval for metrics of %s day/s.", INTERVAL_REPORT_DAYS)

EVALUATION_METRICS_DAYS = int(os.getenv("THOTH_EVALUATION_METRICS_NUMBER_DAYS", 1))
_LOGGER.info("THOTH_EVALUATION_METRICS_NUMBER_DAYS set to %s.", EVALUATION_METRICS_DAYS)

_STORE_HTML = bool(int(os.getenv("THOTH_SLO_REPORTER_STORE_HTML", 0)))

STORE_ON_CEPH = bool(int(os.getenv("THOTH_SLO_REPORTER_STORE_ON_CEPH", 1)))

_SEND_EMAIL = bool(int(os.getenv("THOTH_SLO_REPORTER_SEND_EMAIL", 1)))

_DEBUG_LEVEL = bool(int(os.getenv("DEBUG_LEVEL", 0)))

if _DEBUG_LEVEL:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def check_database_metrics_availability(configuration: Configuration) -> bool:
    """Check database metrics (Prometheus/Thanos) availability."""
    pc = PrometheusConnect(
        url=configuration.thanos_url,
        headers={"Authorization": f"bearer {configuration.thanos_token}"},
        disable_ssl=True,
    )
    response = pc._session.get(
        "{0}/".format(pc.url),
        verify=pc.ssl_verification,
        headers=pc.headers,
        params={},
    )
    if not response.ok:
        return False

    return True


def collect_metrics(configuration: Configuration, sli_report: SLIReport):
    """Collect metrics from Prometheus/Thanos."""
    pc = None

    if not _DRY_RUN:
        pc = PrometheusConnect(
            url=configuration.thanos_url,
            headers={"Authorization": f"bearer {configuration.thanos_token}"},
            disable_ssl=True,
        )

    collected_info: Dict[str, Any] = {}

    for sli_name, sli_methods in sli_report.report_sli_context.items():
        _LOGGER.info(f"Retrieving data for... {sli_name}")
        collected_info[sli_name] = {}

        queries = sli_methods["query"]

        if not queries:
            _LOGGER.warning(f"No queries to be executed for {sli_name} class!")
            continue

        for query_name, query_inputs in queries.items():

            requires_range = False

            if isinstance(query_inputs, dict):
                query = query_inputs["query"]
                requires_range = query_inputs["requires_range"]
                action_type = query_inputs["type"]
            else:
                query = query_inputs

            _LOGGER.info(f"Querying... {query_name}")
            _LOGGER.info(f"Using query... {query}")

            try:
                if not _DRY_RUN:

                    if requires_range:
                        metric_data = pc.custom_query_range(  # type: ignore
                            query=query,
                            start_time=configuration.start_time,
                            end_time=configuration.end_time,
                            step=configuration.step,
                        )

                    else:
                        metric_data = pc.custom_query(query=query)  # type: ignore

                    _LOGGER.info(f"Metric obtained... {metric_data}")

                    if requires_range:
                        metrics_vector = [float(v[1]) for v in metric_data[0]["values"] if float(v[1]) > 0]
                        result = manipulate_retrieved_metrics_vector(metrics_vector=metrics_vector, action=action_type)

                        collected_info[sli_name][query_name] = result

                    else:
                        collected_info[sli_name][query_name] = float(metric_data[0]["value"][1])

                else:
                    metric_data = [{"metric": "dry run", "value": [datetime.datetime.utcnow(), 0]}]
                    result = float(metric_data[0]["value"][1])
                    collected_info[sli_name][query_name] = result

            except Exception as e:
                _LOGGER.exception(f"Could not gather metric for {sli_name}-{query_name}...{e}")
                pass
                collected_info[sli_name][query_name] = "ErrorMetricRetrieval"

    return collected_info


def store_sli_periodic_metrics_to_ceph(
    periodic_metrics: Dict[str, Any],
    configuration: Configuration,
    sli_report: SLIReport,
):
    """Store weekly metrics to ceph."""
    datetime = str(configuration.end_time.strftime("%Y-%m-%d"))
    sli_metrics_id = f"sli-thoth-{datetime}"
    if STORE_ON_CEPH:
        _LOGGER.info(f"Start storing Thoth weekly SLI metrics for {sli_metrics_id}.")

    public_ceph_sli = connect_to_ceph(
        ceph_bucket_prefix=configuration.ceph_bucket_prefix,
        environment=configuration.environment,
        bucket=configuration.public_ceph_bucket,
    )

    for metric_class in periodic_metrics:
        evaluation_method = sli_report.report_sli_context[metric_class]["df_method"]
        inputs_for_df_sli = evaluation_method(
            periodic_metrics[metric_class],
            datetime=datetime,
            timestamp=configuration.end_time_epoch,
        )

        metrics_df = pd.DataFrame(pd.json_normalize(inputs_for_df_sli))

        if metrics_df.empty:
            _LOGGER.warning(f"No data to be stored for {metric_class} class!")
            continue

        csv_columns = sli_report.report_sli_context_columns[metric_class]

        if [c for c in metrics_df.columns.values] != csv_columns:
            raise Exception(
                f"Data stored on Ceph {metrics_df.columns} should be stored with correct columns: {csv_columns}",
            )

        _LOGGER.info(f"Storing... \n{metrics_df}")
        ceph_path = f"{metric_class}/{metric_class}-{datetime}.csv"

        if STORE_ON_CEPH:
            try:
                store_thoth_sli_on_ceph(
                    ceph_sli=configuration.ceph_sli,
                    metric_class=metric_class,
                    metrics_df=metrics_df,
                    ceph_path=ceph_path,
                )
            except Exception as e_ceph:
                _LOGGER.exception(f"Could not store metrics on Thoth bucket on Ceph...{e_ceph}")
                pass

            if configuration.public_ceph_bucket:
                try:
                    store_thoth_sli_on_ceph(
                        ceph_sli=public_ceph_sli,
                        metric_class=metric_class,
                        metrics_df=metrics_df,
                        ceph_path=ceph_path,
                        is_public=True,
                    )
                except Exception as e_ceph:
                    _LOGGER.exception(f"Could not store metrics on Public bucket on Ceph...{e_ceph}")
                    pass
            else:
                _LOGGER.warning("Public bucket to store data is not set!")


def push_thoth_sli_periodic_metrics(
    periodic_metrics: Dict[str, Metric],
    configuration: Configuration,
    sli_report: SLIReport,
):
    """Push Thoth SLI weekly metric to PushGateway."""
    for sli_type, metric_data in periodic_metrics.items():

        for metric_name, weekly_value_metric in metric_data.items():

            if weekly_value_metric != "ErrorMetricRetrieval":

                configuration.thoth_weekly_sli.labels(sli_type=sli_type, metric_name=metric_name, env=configuration.deployment_name,).set(
                    weekly_value_metric,
                )
                _LOGGER.info("(sli_type=%r, metric_name=%r)=%r", sli_type, metric_name, weekly_value_metric)

    push_to_gateway(
        configuration.pushgateway_endpoint,
        job="Weekly Thoth SLI",
        registry=configuration.prometheus_registry,
    )
    _LOGGER.info("Pushed Thoth weekly SLI to Prometheus Pushgateway.")


def generate_email(sli_metrics: Dict[str, Any], sli_report: SLIReport) -> str:
    """Generate email to be sent."""
    message = sli_report.report_start
    message += sli_report.report_style
    message += sli_report.report_intro

    for sli_name, metric_data in sli_metrics.items():

        _LOGGER.debug(f"Generating report for: {sli_name}")

        report_method = sli_report.report_sli_context[sli_name]["report_method"]
        message += "\n" + report_method(metric_data)

    message += sli_report.report_references

    message += sli_report.report_end

    _LOGGER.debug(f"Email message: {message}")

    if _STORE_HTML:
        html_file = open(Path.cwd().joinpath("thoth", "slo_reporter", "SLO-reporter.html"), "w")
        html_file.write(message)
        html_file.close()

    if _DRY_RUN:
        return message

    return message


def send_sli_email(email_message: str, configuration: Configuration, sli_report: SLIReport, using_tls: bool = False):
    """Send email about Thoth Service Level Objectives."""
    msg = MIMEMultipart()
    msg["Subject"] = sli_report.report_subject
    msg["From"] = configuration.sender_address
    msg["To"] = configuration.address_recipients

    _LOGGER.info(f"Address recipient: {configuration.address_recipients}.")

    html_message = MIMEText(email_message, "html")
    msg.attach(html_message)

    if using_tls:
        return send_sli_email_through_smtplib_tls(
            email_message=msg,
            configuration=configuration,
        )

    return _send_email_through_smtplib(
        email_message=msg,
        configuration=configuration,
    )


def send_sli_email_through_smtplib_tls(email_message: MIMEMultipart, configuration: Configuration):
    """Send email using smtplib with TLS."""
    _LOGGER.info(f"Using {configuration.server_host} with port {configuration.server_host_port} server to send email.")

    smtp_username = configuration.smtp_username
    if not smtp_username:
        raise Exception("SMTP_SERVER_USERNAME env variable is not set.")

    smtp_password = configuration.smtp_password
    if not smtp_password:
        raise Exception("SMTP_SERVER_PASSWORD env variable is not set.")

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(host=configuration.server_host, port=configuration.server_host_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.sendmail(configuration.sender_address, configuration.address_recipients, email_message.as_string())
            server.close()
            _LOGGER.info(
                f"Email sent successfully through {configuration.server_host}" f" with port {configuration.server_host_port} server.",
            )
    except Exception as e:
        _LOGGER.info(
            f"Exception when sending email using {configuration.server_host}" f" with port{configuration.server_host_port} server: %s\n" % e,
        )


def _send_email_through_smtplib(email_message: MIMEMultipart, configuration: Configuration):
    """Send email using smtplib library."""
    server = configuration.server_host
    mail_server = smtplib.SMTP(server)
    try:
        mail_server.sendmail(configuration.sender_address, configuration.address_recipients, email_message.as_string())
        _LOGGER.info(
            f"Email sent successfully through {configuration.server_host} server.",
        )
        mail_server.close()
    except Exception as e:
        _LOGGER.info(
            f"Exception when sending email using {configuration.server_host} server: %s\n" % e,
        )


def run_slo_reporter(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    number_days: int,
    dry_run: bool,
    day_of_week: str,
) -> None:
    """Run SLO reporter."""
    configuration = Configuration(start_time=start_time, end_time=end_time, number_days=number_days, dry_run=dry_run)

    if not _DRY_RUN:
        ## Check Database availability
        is_database_available = check_database_metrics_availability(configuration=configuration)

        if not is_database_available:
            raise Exception(f"Thanos endpoint {configuration.thanos_url} is not available! SLO-reporter cannot run.")

    sli_report = SLIReport(configuration=configuration)

    # Collect metrics.
    sli_values_map = collect_metrics(configuration=configuration, sli_report=sli_report)

    # Store metrics on Ceph and push them to Pushgateway.
    if not _DRY_RUN:
        store_sli_periodic_metrics_to_ceph(
            periodic_metrics=sli_values_map,
            configuration=configuration,
            sli_report=sli_report,
        )

        try:
            push_thoth_sli_periodic_metrics(sli_values_map, configuration=configuration, sli_report=sli_report)
        except Exception as e_pushgateway:
            _LOGGER.exception(f"Could not push metrics to Pushgateway...{e_pushgateway}")
            pass

    if _DRY_RUN:
        email_message = generate_email(sli_values_map, sli_report=sli_report)
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
            url = "file://" + f.name
            f.write(email_message)

        webbrowser.open(url)
        return

    email_message = generate_email(sli_values_map, sli_report=sli_report)
    # Generate HTML for email from metrics and send it.
    if not _DRY_RUN and _SEND_EMAIL:
        if day_of_week == configuration.email_day:
            _LOGGER.info(f"Today is: {day_of_week}, therefore I send email.")
            send_sli_email(
                email_message,
                configuration=configuration,
                sli_report=sli_report,
                using_tls=configuration.using_tls,
            )
        else:
            _LOGGER.info(
                f"Today is: {day_of_week}, I do not send emails. I send email only on {configuration.email_day}",
            )
    _LOGGER.info("SLO-reporter did a good job today and finished successfully!")


def main():
    """Execute the main function for Thoth Service Level Objectives (SLO) Reporter."""
    if not _SEND_EMAIL:
        _LOGGER.info("THOTH_SLO_REPORTER_SEND_EMAIL set to 0, no emails will be sent out.")

    if not STORE_ON_CEPH:
        _LOGGER.info("THOTH_SLO_REPORTER_STORE_ON_CEPH set to 0, data won't be stored on Ceph.")

    if _DEBUG_LEVEL:
        _LOGGER.info("SLO reporter running in debug mode.")

    if _DRY_RUN:
        _LOGGER.info("Dry run mode...")

    if EVALUATION_METRICS_DAYS == 0:
        _LOGGER.info("No range of days to be collected, set THOTH_EVALUATION_METRICS_NUMBER_DAYS at least to 1.")

    if EVALUATION_METRICS_DAYS > 1 and _SEND_EMAIL:
        raise Exception(
            "You need to set THOTH_SLO_REPORTER_SEND_EMAIL to 0 if you want to evaluate metrics for more than one day."
            f" Otherwise multiple emails (in this case {EVALUATION_METRICS_DAYS}) will be sent out.",
        )

    for i in range(0, EVALUATION_METRICS_DAYS):
        end_time = datetime.datetime.utcnow() - datetime.timedelta(days=i)
        start_time = end_time - datetime.timedelta(days=INTERVAL_REPORT_DAYS)
        _LOGGER.info(f"Interval: {start_time.strftime('%Y-%m-%d')} - {end_time.strftime('%Y-%m-%d')}")

        day_of_week = end_time.strftime("%A")

        run_slo_reporter(
            start_time=start_time,
            end_time=end_time,
            number_days=INTERVAL_REPORT_DAYS,
            dry_run=_DRY_RUN,
            day_of_week=day_of_week,
        )


if __name__ == "__main__":
    main()
