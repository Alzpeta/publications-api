# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from oarepo_communities.search import CommunitySearch


class ArticleRecordsSearch(CommunitySearch):
    """Article collection search."""
    LIST_SOURCE_FIELDS = [
        'id', 'oarepo:validity.valid', 'oarepo:draft',
        'title', 'dateIssued', 'creator', 'created', 'resourceType',
        'contributor', 'keywords', 'subject', 'abstract', 'state',
        '_primary_community', '_communities',
        '$schema'
    ]
    HIGHLIGHT_FIELDS = {
        'title.cs': None,
        'title._': None,
        'title.en': None
    }