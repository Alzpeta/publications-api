# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from elasticsearch_dsl import Q
from invenio_records_rest.query import default_search_factory
from oarepo_communities.search import CommunitySearch


def article_search_factory(self, search, query_parser=None):
    search, kwargs = default_search_factory(self, search, query_parser)
    search = search.source(['id', 'oarepo:validity.valid', 'title', 'created',
                            'creator', 'abstract'])
    search = search.highlight('*')
    return search, kwargs


class ArticleRecordsSearch(CommunitySearch):
    """Article collection search."""


class MineRecordsSearch(ArticleRecordsSearch):
    class Meta:
        doc_types = ['_doc']
        facets = {}
        default_anonymous_filter = Q('match_none')

        @staticmethod
        def default_filter_factory(search=None, **kwargs):
            return MineRecordsSearch.Meta.default_anonymous_filter
