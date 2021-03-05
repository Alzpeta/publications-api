# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from flask_security.utils import _
from invenio_records_rest.facets import range_filter, terms_filter
from invenio_records_rest.utils import allow_all, deny_all, check_elasticsearch
from invenio_search import RecordsSearch
from oarepo_multilingual import language_aware_text_match_filter
from oarepo_records_draft import DRAFT_IMPORTANT_FILTERS
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from invenio_records_rest.facets import terms_filter, range_filter
from invenio_records_rest.utils import allow_all, deny_all, check_elasticsearch
from invenio_search import RecordsSearch
from oarepo_multilingual import language_aware_text_match_filter
from oarepo_records_draft import DRAFT_IMPORTANT_FACETS, DRAFT_IMPORTANT_FILTERS
from oarepo_ui import translate_facets, translate_filters, translate_facet

from publications.articles.constants import ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE, ARTICLE_ALL_PID_TYPE
from publications.articles.record import AllArticlesRecord
from publications.indexer import CommitingRecordIndexer
from publications.search import FilteredRecordsSearch

RECORDS_DRAFT_ENDPOINTS = {
    'publications/articles': {
        'draft': 'draft-publications/articles',

        'pid_type': ARTICLE_PID_TYPE,
        'pid_minter': 'publications-article',
        'pid_fetcher': 'publications-article',
        'default_endpoint_prefix': True,

        'record_class': 'publications.articles.record.ArticleRecord',

        # TODO: implement proper permissions
        # Who can publish a draft article record
        'publish_permission_factory_imp': allow_all,
        # Who can unpublish (delete published & create a new draft version of)
        # a published article record
        'unpublish_permission_factory_imp': allow_all,
        # Who can edit (create a new draft version of) a published dataset record
        'edit_permission_factory_imp': allow_all,
        # Who can enumerate published articles
        'list_permission_factory_imp': allow_all,
        # Who can view a detail of an existing published article
        'read_permission_factory_imp': allow_all,
        # Make sure everything else is for biden
        'create_permission_factory_imp': allow_all,
        'update_permission_factory_imp': allow_all,
        'delete_permission_factory_imp': allow_all,

        'default_media_type': 'application/json',
        'indexer_class': CommitingRecordIndexer,
        #'search_index': 'oarepo-demo-s3-articles-publication-article-v1.0.0',
        'search_index': 'articles-publication-article-v1.0.0',
        'search_class': RecordsSearch,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },

        'list_route': '/publications/articles/',
        'files': dict(
            # File attachments are currently not allowed on article records
            put_file_factory=allow_all,
            get_file_factory=allow_all,
            delete_file_factory=allow_all
        )
    },
    'draft-publications/articles': {
        'pid_type': ARTICLE_DRAFT_PID_TYPE,
        'record_class': 'publications.articles.record.ArticleDraftRecord',
        #'search_index': 'oarepo-demo-s3-draft-publication-article-v1.0.0',
        'search_index': 'draft-articles-publication-article-v1.0.0',
        'search_class': FilteredRecordsSearch,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },

        # Who can create a new draft article record?
        # TODO: owner of the dataset referenced in article create request?
        # TODO: IMPORTANT!!! harden all permissions
        'create_permission_factory_imp': allow_all,
        # Who can edit an existing draft article record
        'update_permission_factory_imp': allow_all,
        # Who can view an existing draft article record
        'read_permission_factory_imp': allow_all,
        # Who can delete an existing draft article record
        'delete_permission_factory_imp': allow_all,
        # Who can enumerate a draft article record collection
        'list_permission_factory_imp': allow_all,

        'record_loaders': {
            'application/json-patch+json': 'oarepo_validate.json_files_loader',
            'application/json': 'oarepo_validate.json_files_loader'
        },
        'files': dict(
            # File attachments are currently not allowed on article records
            put_file_factory=allow_all,
            get_file_factory=allow_all,
            delete_file_factory=allow_all
        )
    }
}

RECORDS_REST_ENDPOINTS = {
    # readonly url for both endpoints, does not have item route
    # as it is accessed from the endpoints above
    'publications/all-articles': dict(
        record_class=AllArticlesRecord,
        pid_type=ARTICLE_ALL_PID_TYPE,
        pid_minter='all-publications-articles',
        pid_fetcher='all-publications-articles',
        default_endpoint_prefix=True,
        search_class=FilteredRecordsSearch,
        search_index='all-articles',
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        list_route='/publications/all-articles/',
        default_media_type='application/json',
        max_result_window=10000,

        # not used really
        item_route='/publications/all-articles/not-used-but-must-be-present',
        create_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all,
        update_permission_factory_imp=allow_all,
        read_permission_factory_imp=check_elasticsearch,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        search_factory_imp='publications.articles.search:article_search_factory'
    )
}
def boolean_filter(field):
    def val2bool(x):
        if x == '1' or x == 'true' or x is True:
            return True
        return False

    def inner(values):
        return Q('terms', **{field: [val2bool(x) for x in values]})

    return inner


def date_year_range(field, start_date_math=None, end_date_math=None, **kwargs):
    def inner(values):
        range_values = [f'{v}-01--{v}-12' for v in values]
        return range_filter(field, start_date_math, end_date_math, **kwargs)(range_values)

    return inner


def state_terms_filter(field):
    def inner(values):
        if 'filling' in values:
            return Bool(should=[
                Q('terms', **{field: values}),
                Bool(
                    must_not=[
                        Q('exists', field='state')
                    ]
                )
            ], minimum_should_match=1)
        else:
            return Q('terms', **{field: values})

    return inner


FILTERS = {
    _('category'): terms_filter('category'),
    _('creator'): terms_filter('creator.raw'),
    _('title'): language_aware_text_match_filter('titles'),
    _('state'): state_terms_filter('state'),
    # draft
    **DRAFT_IMPORTANT_FILTERS
}


def term_facet(field, order='desc', size=100, missing=None):
    ret = {
        'terms': {
            'field': field,
            'size': size,
            "order": {"_count": order}
        },
    }
    if missing is not None:
        ret['terms']['missing'] = missing
    return ret


FACETS = {
    'state': translate_facet(term_facet('state', missing='filling'), possible_values=[
        _('filling'),
        _('approving'),
        _('approved'),
        _('published'),
        _('deleted')
    ]),
    'creator': term_facet('creator.raw'),
    **DRAFT_IMPORTANT_FACETS
}

RECORDS_REST_FACETS = {
    'draft-articles-publication-article-v1.0.0': {
        'aggs': translate_facets(FACETS, label='{facet_key}', value='{value_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
    'articles-publication-article-v1.0.0': {
        'aggs': translate_facets(FACETS, label='{facet_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
    'all-articles': {
        'aggs': translate_facets(FACETS, label='{facet_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
}

RECORDS_REST_SORT_OPTIONS = {
    'all-articles': {
        'alphabetical': {
            'title': 'alphabetical',
            'fields': [
                'titles.cs.raw'
            ],
            'default_order': 'asc',
            'order': 1
        },
        'best_match': {
            'title': 'Best match',
            'fields': ['_score'],
            'default_order': 'desc',
            'order': 1,
        }
    }
}

RECORDS_REST_DEFAULT_SORT = {
    'all-articles': {
        'query': 'best_match',
        'noquery': 'alphabetical'
    }
}
