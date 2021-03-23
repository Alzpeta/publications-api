# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from invenio_records_rest.facets import terms_filter, range_filter
from invenio_records_rest.utils import allow_all, deny_all
from oarepo_communities.links import community_record_links_factory
from oarepo_multilingual import language_aware_text_match_filter
from oarepo_records_draft import DRAFT_IMPORTANT_FACETS, DRAFT_IMPORTANT_FILTERS
from oarepo_ui import translate_facets, translate_filters, translate_facet

from publications.datasets.constants import DATASET_DRAFT_PID_TYPE, DATASET_PID_TYPE, DATASET_ALL_PID_TYPE, \
    DATASET_RECORD_CLASS, DATASET_DRAFT_RECORD_CLASS, DATASET_ALL_RECORD_CLASS
from publications.datasets.record import published_index_name, draft_index_name, all_index_name
from publications.datasets.search import DatasetRecordsSearch
from publications.indexer import CommitingRecordIndexer

_ = lambda x: x

RECORDS_DRAFT_ENDPOINTS = {
    'publications/datasets': {
        'draft': 'draft-publications/datasets',

        'pid_type': DATASET_PID_TYPE,
        'pid_minter': 'publications-dataset',
        'pid_fetcher': 'publications-dataset',
        'default_endpoint_prefix': True,

        'record_class': DATASET_RECORD_CLASS,
        'links_factory_imp': community_record_links_factory,

        # Who can publish a draft dataset record
        'publish_permission_factory_imp': 'publications.datasets.permissions.publish_draft_object_permission_impl',
        # Who can unpublish (delete published & create a new draft version of)
        # a published dataset record
        'unpublish_permission_factory_imp': 'publications.datasets.permissions.unpublish_draft_object_permission_impl',
        # Who can edit (create a new draft version of) a published dataset record
        'edit_permission_factory_imp': 'publications.datasets.permissions.update_object_permission_impl',
        # Who can enumerate published dataset record collection
        'list_permission_factory_imp': allow_all,
        # Who can view an existing published dataset record detail
        'read_permission_factory_imp': allow_all,
        # Make sure everything else is for biden
        'create_permission_factory_imp': deny_all,
        'update_permission_factory_imp': deny_all,
        'delete_permission_factory_imp': deny_all,

        'default_media_type': 'application/json',
        'indexer_class': CommitingRecordIndexer,
        'search_class': DatasetRecordsSearch,
        'search_index': published_index_name,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },

        'list_route': '/<community_id>/datasets/published/',  # will not be used really
        'item_route':
            f'/<commpid({DATASET_PID_TYPE},model="datasets",record_class="{DATASET_RECORD_CLASS}"):pid_value>',
        'files': dict(
            # Who can upload attachments to a draft dataset record
            put_file_factory=deny_all,
            # Who can download attachments from a draft dataset record
            get_file_factory=allow_all,
            # Who can delete attachments from a draft dataset record
            delete_file_factory=deny_all
        )
    },
    'draft-publications/datasets': {
        'pid_type': DATASET_DRAFT_PID_TYPE,
        'search_class': DatasetRecordsSearch,
        'search_index': draft_index_name,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },
        'record_serializers': {
            'application/json': 'oarepo_validate:json_response',
        },
        'record_class': DATASET_DRAFT_RECORD_CLASS,
        'links_factory_imp': community_record_links_factory,

        # Who can create a new draft dataset record
        'create_permission_factory_imp': 'publications.datasets.permissions.create_draft_object_permission_impl',
        # Who can edit an existing draft dataset record
        'update_permission_factory_imp': 'publications.datasets.permissions.update_draft_object_permission_impl',
        # Who can view an existing draft dataset record
        'read_permission_factory_imp': 'publications.datasets.permissions.read_draft_object_permission_impl',
        # Who can delete an existing draft dataset record
        'delete_permission_factory_imp': 'publications.datasets.permissions.delete_draft_object_permission_impl',
        # Who can enumerate a draft dataset record collection
        'list_permission_factory_imp': 'publications.datasets.permissions.list_draft_object_permission_impl',

        'list_route': '/<community_id>/datasets/draft/',
        'item_route':
            f'/<commpid({DATASET_DRAFT_PID_TYPE},model="datasets/draft",record_class="{DATASET_DRAFT_RECORD_CLASS}"):pid_value>',
        'record_loaders': {
            'application/json': 'oarepo_validate.json_files_loader',
            'application/json-patch+json': 'oarepo_validate.json_loader'
        },
        'files': dict(
            # Who can upload attachments to a draft dataset record
            put_file_factory='publications.datasets.permissions.put_draft_file_permission_impl',
            # Who can download attachments from a draft dataset record
            get_file_factory='publications.datasets.permissions.get_draft_file_permission_impl',
            # Who can delete attachments from a draft dataset record
            delete_file_factory='publications.datasets.permissions.delete_draft_file_permission_impl'
        )
    }
}

RECORDS_REST_ENDPOINTS = {
    # readonly url for both endpoints, does not have item route
    # as it is accessed from the endpoints above
    'publications/all-datasets': dict(
        pid_type=DATASET_ALL_PID_TYPE,
        pid_minter='all-publications-datasets',
        pid_fetcher='all-publications-datasets',
        default_endpoint_prefix=True,
        record_class=DATASET_ALL_RECORD_CLASS,
        search_class=DatasetRecordsSearch,
        search_index=all_index_name,
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        list_route='/<community_id>/datasets/',
        links_factory_imp=community_record_links_factory,
        default_media_type='application/json',
        max_result_window=10000,
        # not used really
        item_route=f'/datasets'
                   f'/not-used-but-must-be-present',
        list_permission_factory_imp='publications.datasets.permissions.list_all_object_permission_impl',
        create_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        read_permission_factory_imp=deny_all,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        use_options_view=False
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
    draft_index_name: {
        'aggs': translate_facets(FACETS, label='{facet_key}', value='{value_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
    published_index_name: {
        'aggs': translate_facets(FACETS, label='{facet_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
    all_index_name: {
        'aggs': translate_facets(FACETS, label='{facet_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
}

RECORDS_REST_SORT_OPTIONS = {
    all_index_name: {
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
    all_index_name: {
        'query': 'best_match',
        'noquery': 'alphabetical'
    }
}
