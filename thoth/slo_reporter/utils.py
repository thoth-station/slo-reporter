#!/usr/bin/env python3
# thoth-slo-reporter
# Copyright(C) 2020, 2021 Francesco Murdaca
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

"""Collection of methods used in SLO-reporter."""

import logging
import statistics
import datetime

from io import StringIO

import pandas as pd
import numpy as np

from typing import List, Dict, Optional, Any

from thoth.storages import CephStore

from thoth.slo_reporter.configuration import Configuration, _get_sli_metrics_prefix

_LOGGER = logging.getLogger(__name__)


def manipulate_retrieved_metrics_vector(metrics_vector: List[float], action: str) -> float:
    """Manipulate metrics vector obtained from Prometheus/Thanos depending on the requested result type.

    :parameter: metrics_vector: metrics vector
    :parameter: action: Type of manipulation on metrics vector to obtain the final metric.
    - `min_max` -> Difference between max and min value in vector.
    - `min_max_only_ascending` -> Difference between max and min value in vector
        verifying all values retrieved are in ascending order otherwise they are removed.
    - `average` -> Average value of vector without 0 values.
    - `latest` -> Latest value of vector different from 0.

    :output: metric/SLI
    """
    # Make sure 0 results are not considered
    metric = 0.0
    if not metrics_vector:
        return metric

    if action == "min_max":
        metric = max(metrics_vector) - min(metrics_vector)

    elif action == "delta":
        modified_results = _evaluate_ascending_results(metrics_vector=metrics_vector)
        metric = metrics_vector[-1] - metrics_vector[0]

    elif action == "min_max_only_ascending":
        modified_results = _evaluate_ascending_results(metrics_vector=metrics_vector)
        metric = max(modified_results) - min(modified_results)

    elif action == "average":
        metric = statistics.mean(metrics_vector)

    elif action == "latest":
        metric = metrics_vector[-1]

    return metric


def _evaluate_ascending_results(metrics_vector: List[float]) -> List[float]:
    """Evaluate vector with only ascending values."""
    counter = 0
    modified_vector = []

    for retrieved_value in metrics_vector:
        if counter == 0:
            modified_vector.append(retrieved_value)

        else:

            if retrieved_value > metrics_vector[counter - 1]:
                modified_vector.append(retrieved_value)

            else:
                pass

        counter += 1

    return modified_vector


def evaluate_change(old_value: float, new_value: float, is_storing: bool = False) -> str:
    """Evaluate difference for report."""
    diff = new_value - old_value

    sign = ""

    if np.isnan(diff):
        diff = new_value

    if is_storing:
        if diff.is_integer():
            return "{:.2f}".format(diff)
        else:
            return "{:.0f}".format(diff)

    if diff > 0:
        sign = "+"

    if isinstance(diff, float):
        if diff.is_integer():
            change = sign + "{:.0f}".format(diff)
        else:
            change = sign + "{:.2f}".format(diff)

    else:
        change = sign + "{:.0f}".format(diff)

    return change


def process_html_inputs(
    html_inputs: Dict[str, Any],
    sli_name: str,
    last_period_time: datetime.datetime,
    ceph_sli: CephStore,
    sli_columns: List[str],
    store_columns: List[str],
    is_storing: bool = False,
) -> Dict[str, Any]:
    """Process HTML inputs."""
    sli_path = f"{sli_name}/{sli_name}-{last_period_time}.csv"
    last_week_data = retrieve_thoth_sli_from_ceph(ceph_sli, sli_path, store_columns)

    for c in sli_columns:

        if not last_week_data.empty:
            old_value = last_week_data[c].values[0]
            change = evaluate_change(old_value=old_value, new_value=html_inputs[c]["value"], is_storing=is_storing)
            html_inputs[c]["change"] = change

        else:
            if is_storing:
                html_inputs[c]["change"] = np.nan
            else:
                html_inputs[c]["change"] = "N/A"

    return html_inputs


def connect_to_ceph(ceph_bucket_prefix: str, environment: str, bucket: Optional[str] = None) -> CephStore:
    """Connect to Ceph to store SLI metrics for Thoth."""
    prefix = _get_sli_metrics_prefix(ceph_bucket_prefix=ceph_bucket_prefix, environment=environment)
    ceph = CephStore(prefix=prefix, bucket=bucket)
    ceph.connect()

    return ceph


def store_thoth_sli_on_ceph(
    ceph_sli: CephStore, metric_class: str, metrics_df: pd.DataFrame, ceph_path: str, is_public: bool = False,
) -> None:
    """Store Thoth SLI on Ceph."""
    metrics_csv = metrics_df.to_csv(index=False, sep="`", header=False)

    if is_public:
        _LOGGER.info(f"Storing on public bucket... {ceph_path}")

    else:
        _LOGGER.info(f"Storing on private bucket... {ceph_path}")

    ceph_sli.store_blob(blob=metrics_csv, object_key=ceph_path)
    _LOGGER.info(f"Succesfully stored Thoth weekly SLI metrics for {metric_class} at {ceph_path}")


def retrieve_thoth_sli_from_ceph(ceph_sli: CephStore, ceph_path: str, total_columns: List[str]) -> pd.DataFrame:
    """Retrieve Thoth SLI from Ceph."""
    _LOGGER.info(f"Retrieving... \n{ceph_path}")
    try:
        retrieved_data = ceph_sli.retrieve_blob(object_key=ceph_path).decode('utf-8')
        data = StringIO(retrieved_data)
        _LOGGER.debug(f"retrieved data:\n {data}")
        last_data = pd.read_csv(data, names=total_columns, sep="`")

    except Exception as e:
        _LOGGER.warning(f"No file could be retrieved from Ceph: {e}")
        last_data = pd.DataFrame(columns=total_columns)

    return last_data


def evaluate_total_data_window_days(
    sli_name: str,
    total_columns: List[str],
    quantity: str,
    configuration: Configuration,
):
    """Evaluate weekly data for adviser inputs."""
    html_inputs: Dict[str, Any] = {}
    total_quantity: Dict[str, Any] = {}

    number_days = configuration.adviser_inputs_analysis_days

    delta = datetime.timedelta(days=1)

    if not configuration.dry_run:

        e_time = configuration.start_time.strftime('%Y-%m-%d').split("-")
        current_end_time = datetime.date(year=int(e_time[0]), month=int(e_time[1]), day=int(e_time[2]))
        + datetime.timedelta(days=1)
        current_initial_date = current_end_time  - datetime.timedelta(days=number_days)

        while current_initial_date < current_end_time:

            _LOGGER.info(f"Analyzing for start date: {current_initial_date}")

            sli_path = f"{sli_name}/{sli_name}-{current_initial_date}.csv"
            daily_quantity_df = retrieve_thoth_sli_from_ceph(
                configuration.ceph_sli,
                sli_path,
                [c for c in total_columns if c != "timestamp"],
            )

            for parameter in daily_quantity_df[quantity].unique():
                subset_df = daily_quantity_df[daily_quantity_df[quantity] == parameter]
                if parameter not in total_quantity:
                    total_quantity[parameter] = subset_df["total"].values[0]
                else:
                    total_quantity[parameter] += subset_df["total"].values[0]

            current_initial_date += delta

        total_ = 0
        for _, total_counts in total_quantity.items():
            total_ += total_counts

        for quantity__, total_counts in total_quantity.items():
            html_inputs[quantity__] = {}

            if not total_counts:
                html_inputs[quantity__]["new"] = 0
                html_inputs[quantity__]["percentage"] = 0
            else:
                percentage = total_counts / total_
                html_inputs[quantity__]["new"] = "+" + "{:.0f}".format(total_counts)
                html_inputs[quantity__]["percentage"] = abs(round(percentage * 100, 3))

    return html_inputs
