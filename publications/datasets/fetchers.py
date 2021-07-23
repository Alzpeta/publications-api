# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from invenio_pidstore.fetchers import FetchedPID

from publications.datasets.constants import DATASET_DRAFT_PID_TYPE
from publications.datasets.minters import DatasetProvider


def dataset_fetcher(record_uuid, data):
    """Fetch an object publications PID.

    :param record_uuid: Record UUID.
    :param data: Record content.
    :returns: A :class:`invenio_pidstore.fetchers.FetchedPID` that contains
        data['did'] as pid_value.
    """
    return FetchedPID(
        provider=DatasetProvider,
        pid_type=DatasetProvider.pid_type,
        pid_value=data['id']
    )


def dataset_all_fetcher(record_uuid, data):
    fetched_pid = dataset_fetcher(record_uuid, data)
    if 'oarepo:validity' in data:
        return FetchedPID(
            provider=fetched_pid.provider,
            pid_type=DATASET_DRAFT_PID_TYPE,
            pid_value=fetched_pid.pid_value,
        )
    else:
        return fetched_pid
