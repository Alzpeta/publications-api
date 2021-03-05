# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from invenio_records_rest.query import default_search_factory
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from flask import request
from invenio_search import RecordsSearch
import traceback
from publications.permissions import MODIFICATION_ROLE_PERMISSIONS

def article_search_factory(self, search, query_parser=None):
    search, kwargs = default_search_factory(self, search, query_parser)
    search = search.source(['id', 'oarepo:validity.valid', 'title', 'created',
                            'creator', 'abstract'])
    search = search.highlight('*')
    return search, kwargs
class ArticleRecordsSearch(RecordsSearch):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._source = [
            'id', 'oarepo:validity.valid', 'oarepo:draft', 'abstract', 'title', 'created']
        self._highlight['title.cs'] = {}
        self._highlight['title._'] = {}
        self._highlight['title.en'] = {}
        self._highlight['abstract.cs'] = {}
        self._highlight['abstract._'] = {}
        self._highlight['abstract.en'] = {}

    class Meta:
        doc_types = ['_doc']

        default_anonymous_filter = Q('term', state='published')
        default_authenticated_filter = Q('terms', state=['approved', 'published'])

        @staticmethod
        def default_filter_factory(search=None, **kwargs):
            try:
                quick_filter = request.args.get('quick-filter', None)
            except:
                traceback.print_exc()
                quick_filter = None

            if quick_filter == 'mine':
                q = Q('match_none')
            else:
                if MODIFICATION_ROLE_PERMISSIONS.can():
                    # if current user is ingestion user or curator, return all records
                    q = Q('match_all')
                else:
                    # otherwise return approved and published
                    q = ArticleRecordsSearch.Meta.default_authenticated_filter

            if quick_filter == 'filling':
                q = Bool(must=[
                    q,
                    Bool(
                        should=[
                            Q('term', state='filling'),
                            Bool(
                                must_not=[
                                    Q('exists', field='state')
                                ]
                            )
                        ],
                        minimum_should_match=1
                    )
                ])
            elif quick_filter == 'approving':
                q = Bool(must=[
                    q,
                    Q('term', state='approving')
                ])
            elif quick_filter == 'approved':
                q = Bool(must=[
                    q,
                    Q('term', state='approved')
                ])
            elif quick_filter == 'published':
                q = Bool(must=[
                    q,
                    Q('term', state='published')
                ])
            return q

class MineRecordsSearch(ArticleRecordsSearch):
    class Meta:
        doc_types = ['_doc']
        facets = {}
        default_anonymous_filter = Q('match_none')

        @staticmethod
        def default_filter_factory(search=None, **kwargs):
            return MineRecordsSearch.Meta.default_anonymous_filter