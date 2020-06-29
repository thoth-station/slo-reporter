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

"""Collection of methods used in SLO-reporter."""

import logging
import statistics

import pandas as pd

from typing import List, Dict, Optional

from thoth.storages import CephStore

from thoth.slo_reporter.configuration import _get_sli_metrics_prefix


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
    if not metrics_vector:
        metric = 0
        return metric

    if action == "min_max":
        metric = max(metrics_vector) - min(metrics_vector)

    elif action == "min_max_only_ascending":
        counter = 0
        modified_results = []

        for retrieved_value in metrics_vector:
            if counter == 0:
                modified_results.append(retrieved_value)

            else:

                if retrieved_value > metrics_vector[counter - 1]:
                    modified_results.append(retrieved_value)

                else:
                    pass

            counter += 1

        metric = max(modified_results) - min(modified_results)

    elif action == "average":
        metric = statistics.mean(metrics_vector)

    elif action == "latest":
        metric = metrics_vector[-1]

    return metric


def connect_to_ceph(bucket: Optional[str] = None) -> CephStore:
    """Connect to Ceph to store SLI metrics for Thoth."""
    prefix = _get_sli_metrics_prefix()
    ceph = CephStore(prefix=prefix, bucket=bucket)
    ceph.connect()
    return ceph


def store_thoth_sli_on_ceph(
    ceph_sli: CephStore, metric_class: str, metrics_df: pd.DataFrame, ceph_path: str, is_public: bool = False,
) -> None:
    """Store Thoth SLI on Ceph."""
    metrics_csv = metrics_df.to_csv(index=False, header=False)
    if is_public:
        _LOGGER.info(f"Storing on public bucket... {ceph_path}")
    else:
        _LOGGER.info(f"Storing on private bucket... {ceph_path}")
    ceph_sli.store_blob(blob=metrics_csv, object_key=ceph_path)
    _LOGGER.info(f"Succesfully stored Thoth weekly SLI metrics for {metric_class} at {ceph_path}")
