# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import traceback

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from flask import request
from oarepo_communities.search import CommunitySearch


class DatasetRecordsSearch(CommunitySearch):
    """Dataset collection search."""


class MineRecordsSearch(DatasetRecordsSearch):
    class Meta:
        doc_types = ['_doc']
        facets = {}
        default_anonymous_filter = Q('match_none')

        @staticmethod
        def default_filter_factory(search=None, **kwargs):
            return MineRecordsSearch.Meta.default_anonymous_filter
