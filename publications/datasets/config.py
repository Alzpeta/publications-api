# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from elasticsearch_dsl import Q
from invenio_indexer.api import RecordIndexer
from invenio_records_rest.facets import terms_filter, range_filter
from invenio_records_rest.utils import allow_all, deny_all, check_elasticsearch
from invenio_search import RecordsSearch
from oarepo_multilingual import language_aware_text_match_filter

from oarepo_records_draft import DRAFT_IMPORTANT_FACETS, DRAFT_IMPORTANT_FILTERS
from oarepo_ui import translate_facets, translate_filters, translate_facet

from publications.datasets.constants import DATASET_DRAFT_PID_TYPE, DATASET_PID_TYPE, DATASET_ALL_PID_TYPE
from publications.indexer import CommitingRecordIndexer
from publications.permissions import allow_curator, allow_owner, allow_curator_or_owner, allow_authenticated

_ = lambda x: x


RECORDS_DRAFT_ENDPOINTS = {
    'publications/datasets': {
        'draft': 'draft-publications/datasets',

        'pid_type': DATASET_PID_TYPE,
        'pid_minter': 'publications-dataset',
        'pid_fetcher': 'publications-dataset',
        'default_endpoint_prefix': True,

        'record_class': 'publications.datasets.record.DatasetRecord',

        # Who can publish a draft dataset record
        'publish_permission_factory_imp': allow_curator,
        # Who can unpublish (delete published & create a new draft version of)
        # a published dataset record
        'unpublish_permission_factory_imp': allow_curator,
        # Who can edit (create a new draft version of) a published dataset record
        'edit_permission_factory_imp': allow_curator_or_owner,
        # Who can enumerate published dataset record collection
        'list_permission_factory_imp': allow_all,
        # Who can view an existing published dataset record detail
        'read_permission_factory_imp': allow_all,

        'default_media_type': 'application/json',
        'indexer_class': CommitingRecordIndexer,
        'search_index': 'oarepo-demo-s3-datasets-publication-dataset-v1.0.0',

        'list_route': '/publications/datasets/',

        'files': dict(
            # Who can download attachments on a published dataset record
            get_file_factory=allow_all
        )
    },
    'draft-publications/datasets': {
        'pid_type': DATASET_DRAFT_PID_TYPE,
        'search_index': 'oarepo-demo-s3-draft-datasets-publication-dataset-v1.0.0',
        'record_class': 'publications.datasets.record.DatasetDraftRecord',

        # Who can create a new draft dataset record
        'create_permission_factory_imp': allow_authenticated,
        # Who can edit an existing draft dataset record
        'update_permission_factory_imp': allow_owner,
        # Who can view an existing draft dataset record
        'read_permission_factory_imp': allow_curator_or_owner,
        # Who can delete an existing draft dataset record
        'delete_permission_factory_imp': allow_curator_or_owner,
        # Who can enumerate a draft dataset record collection
        'list_permission_factory_imp': allow_authenticated,

        'list_route': '/draft/publications/datasets/',
        'record_loaders': {
            'application/json': 'oarepo_validate.json_files_loader'
        },
        'files': dict(
            # Who can upload attachments to a draft dataset record
            put_file_factory=allow_owner,
            # Who can download attachments from a draft dataset record
            get_file_factory=allow_owner
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
        search_class=RecordsSearch,
        search_index='oarepo-demo-s3-all-datasets',
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        list_route='/publications/all-datasets/',
        default_media_type='application/json',
        max_result_window=10000,

        # not used really
        item_route='/publications/all-datasets/not-used-but-must-be-present',
        create_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        read_permission_factory_imp=check_elasticsearch,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        search_factory_imp='publications.datasets.search:dataset_search_factory'
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


FILTERS = {
    _('category'): terms_filter('category'),
    _('submissionStatus'): terms_filter('submissionStatus'),
    _('creator'): terms_filter('creator.raw'),
    _('title'): language_aware_text_match_filter('title'),

    # draft
    **DRAFT_IMPORTANT_FILTERS
}


def term_facet(field, order='desc', size=100):
    return {
        'terms': {
            'field': field,
            'size': size,
            "order": {"_count": order}
        },
    }


FACETS = {
    'submissionStatus': translate_facet(term_facet('submissionStatus'), possible_values=[
        _('incomplete'),
        _('pending_approval')
    ]),
    'creator': term_facet('creator.raw'),
    **DRAFT_IMPORTANT_FACETS
}

RECORDS_REST_FACETS = {
    'draft-datasets-publication-dataset-v1.0.0': {
        'aggs': translate_facets(FACETS, label='{facet_key}', value='{value_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
    'datasets-publication-dataset-v1.0.0': {
        'aggs': translate_facets(FACETS, label='{facet_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
    'all-publications': {
        'aggs': translate_facets(FACETS, label='{facet_key}'),
        'filters': translate_filters(FILTERS, label='{filter_key}')
    },
}

RECORDS_REST_SORT_OPTIONS = {
    'all-publications': {
        'alphabetical': {
            'title': 'alphabetical',
            'fields': [
                'title.cs.raw'
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
    'all-publications': {
        'query': 'best_match',
        'noquery': 'alphabetical'
    }
}

"""
RECORDS_REST_SORT_OPTIONS = {
    DATASET_DRAFT_SEARCH_INDEX: {
        'bestmatch': {
            'title': 'Best match',
            'fields': ['_score'],
            'default_order': 'desc',
            'order': 1,
        },
        'mostrecent': {
            'title': 'Most recent',
            'fields': ['_created'],
            'default_order': 'asc',
            'order': 2,
        },
        'alphabet': {
            'title': 'A - Z',
            'fields': [
                {
                    'title.value.raw': {
                        "order": "asc",
                        "nested": {
                            "path": "title",
                            "filter": {
                                "term": {"title.lang": "cs"}
                            }
                        }
                    }
                },
                {
                    'title.value.raw': {
                        "order": "asc",
                        "nested": {
                            "path": "title",
                            "filter": {
                                "term": {"title.lang": "en"}
                            }
                        }
                    }
                }
            ],
            'default_order': 'asc',
            'order': 2,
        },
    }
}

RECORDS_REST_DEFAULT_SORT = {
    DATASET_DRAFT_SEARCH_INDEX: {
        'query': 'alphabet',
        'noquery': 'alphabet',
    }
}
"""
