# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_communities.search import CommunitySearch


class DatasetRecordsSearch(CommunitySearch):
    """Dataset collection search."""
    LIST_SOURCE_FIELDS = [
        'id', 'oarepo:validity.valid', 'oarepo:draft',
        'title', 'abstract', 'creator', 'dates', 'resource_type',
        'contributor', 'keywords', 'subject', 'abstract', 'state',
        '_primary_community', '_communities', 'access'
        '$schema'
    ]
    HIGHLIGHT_FIELDS = {
        'title.cs': None,
        'title._': None,
        'title.en': None
    }
