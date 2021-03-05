# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from invenio_pidstore.fetchers import FetchedPID

from publications.articles.constants import ARTICLE_DRAFT_PID_TYPE
from publications.articles.minters import ArticleProvider


def article_fetcher(record_uuid, data):
    """Fetch an work publications PID.

    :param record_uuid: Record UUID.
    :param data: Record content.
    :returns: A :class:`invenio_pidstore.fetchers.FetchedPID` that contains
        data['did'] as pid_value.
    """
    return FetchedPID(
        provider=ArticleProvider,
        pid_type=ArticleProvider.pid_type,
        pid_value=data['id']
    )


def article_all_fetcher(record_uuid, data):
    fetched_pid = article_fetcher(record_uuid, data)
    if 'oarepo:validity' in data:
        return FetchedPID(
            provider=fetched_pid.provider,
            pid_type=ARTICLE_DRAFT_PID_TYPE,
            pid_value=fetched_pid.pid_value,
        )
    else:
        return fetched_pid
