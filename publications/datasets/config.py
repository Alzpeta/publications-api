# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from functools import partial

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from invenio_records_rest.facets import terms_filter, range_filter
from invenio_records_rest.utils import allow_all, deny_all
from oarepo_communities.links import community_record_links_factory
from oarepo_communities.search import community_search_factory
from oarepo_multilingual import language_aware_text_match_filter
from oarepo_records_draft import DRAFT_IMPORTANT_FACETS, DRAFT_IMPORTANT_FILTERS
from oarepo_ui import translate_facets, translate_filters, translate_facet

from publications.datasets.constants import DATASET_DRAFT_PID_TYPE, DATASET_PID_TYPE, DATASET_ALL_PID_TYPE, \
    DATASET_RECORD_CLASS, DATASET_DRAFT_RECORD_CLASS, DATASET_ALL_RECORD_CLASS
from publications.datasets.record import published_index_name, draft_index_name, all_index_name
from publications.datasets.search import DatasetRecordsSearch
from publications.indexer import CommitingRecordIndexer
from publications.links import publications_links_factory
from oarepo_ui.facets import nested_facet, RoleFacets
from oarepo_ui.filters import nested_filter
from oarepo_multilingual import language_aware_text_term_facet, language_aware_text_terms_filter
from oarepo_communities.constants import STATE_PUBLISHED, STATE_EDITING, STATE_APPROVED, STATE_PENDING_APPROVAL, \
    STATE_DELETED

_ = lambda x: x

RECORDS_DRAFT_ENDPOINTS = {
    'datasets': {
        'draft': 'draft-datasets',

        'pid_type': DATASET_PID_TYPE,
        'pid_minter': 'publications-dataset',
        'pid_fetcher': 'publications-dataset',
        'default_endpoint_prefix': True,

        'record_class': DATASET_RECORD_CLASS,
        'links_factory_imp': partial(community_record_links_factory, original_links_factory=publications_links_factory),

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
        'search_factory_imp': community_search_factory,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },
        'record_loaders': {
            'application/json': 'oarepo_validate.json_files_loader',
            'application/json-patch+json': 'oarepo_validate.json_loader'
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
    'draft-datasets': {
        'pid_type': DATASET_DRAFT_PID_TYPE,
        'search_class': DatasetRecordsSearch,
        'search_index': draft_index_name,
        'search_factory_imp': community_search_factory,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },
        'record_serializers': {
            'application/json': 'oarepo_validate:json_response',
        },
        'record_class': DATASET_DRAFT_RECORD_CLASS,
        'links_factory_imp': partial(community_record_links_factory, original_links_factory=publications_links_factory),

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
    'all-community-datasets': dict(
        pid_type=DATASET_ALL_PID_TYPE + '-community-all',
        pid_minter='all-publications-datasets',
        pid_fetcher='all-publications-datasets',
        default_endpoint_prefix=True,
        record_class=DATASET_ALL_RECORD_CLASS,
        search_class=DatasetRecordsSearch,
        search_factory_imp=community_search_factory,
        search_index=all_index_name,
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        record_loaders={
            'application/json': 'oarepo_validate.json_files_loader',
            'application/json-patch+json': 'oarepo_validate.json_loader'
        },
        list_route='/<community_id>/datasets/all/',
        links_factory_imp=partial(community_record_links_factory,
                                  original_links_factory=publications_links_factory),
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
    ),
    'all-datasets': dict(
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
        list_route='/datasets/all/',
        links_factory_imp=partial(community_record_links_factory,
                                  original_links_factory=publications_links_factory),
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
    ),
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


FILTERS = {
    _('state'): state_terms_filter('state'),
    _('keywords'): terms_filter('keywords'),
    _('languages'): nested_filter('languages', language_aware_text_terms_filter('languages.title')),
    _('creators'): nested_filter('creators.person_or_org', terms_filter('creators.person_or_org.name')),
    _('affiliations'): nested_filter('creators.affiliations', terms_filter('creators.affiliations.name')),
    _('rights'): nested_filter('rights', language_aware_text_terms_filter('rights.title')),
    _('title'): language_aware_text_match_filter('title'),
    # draft
    **DRAFT_IMPORTANT_FILTERS
}

FACETS = {
    'state': translate_facet(term_facet('state', missing=STATE_EDITING), possible_values=[
        _(STATE_EDITING),
        _(STATE_PENDING_APPROVAL),
        _(STATE_APPROVED),
        _(STATE_PUBLISHED),
        _(STATE_DELETED)
    ]),
    # 'contributors': nested_facet('contributors', term_facet('contributors.person_or_org.name.raw')),
    'languages': nested_facet('languages', language_aware_text_term_facet('languages.title')),
    'keywords': term_facet('keywords'),
    'affiliations': nested_facet('creators.affiliations', term_facet('creators.affiliations.name')),
    'creators': nested_facet('creators.person_or_org', term_facet('creators.person_or_org.name')),
    'rights': nested_facet('rights', language_aware_text_term_facet('rights.title')),
    **DRAFT_IMPORTANT_FACETS
}


class RoleFacetsDict(RoleFacets, dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def keys(self):
        return self.data.get(self.current_role(), {}).keys()

    def __getitem__(self, key):
        return self.get(key)


RECORDS_REST_FACETS = {
    draft_index_name: dict(
        aggs=translate_facets(FACETS, label='{facet_key}', value='{value_key}'),
        filters=translate_filters(FILTERS, label='{filter_key}')
    ),
    published_index_name: dict(
        aggs=translate_facets(FACETS, label='{facet_key}', value='{value_key}'),
        filters=translate_filters(FILTERS, label='{filter_key}')
    ),
    all_index_name: dict(
        aggs=translate_facets(FACETS, label='{facet_key}', value='{value_key}'),
        filters=translate_filters(FILTERS, label='{filter_key}')
    )
}

RECORDS_REST_SORT_OPTIONS = {
    all_index_name: {
        'alphabetical': {
            'title': 'alphabetical',
            'fields': [
                'state',
                'title.cs.raw',
                'title.en.raw'
            ],
            'default_order': 'asc',
            'order': 1
        },
        'alphabetical_desc': {
            'title': 'alphabetical_desc',
            'fields': [
                'state',
                '-title.cs.raw',
                '-title.en.raw',
            ],
            'default_order': 'desc',
            'order': 1
        },
        'date_created': {
            'title': 'date_created',
            'fields': ['dates'],
            'default_order': 'desc',
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
