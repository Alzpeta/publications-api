# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_records_rest.utils import allow_all, deny_all, check_elasticsearch
from invenio_search import RecordsSearch

from publications.articles.constants import ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE, ARTICLE_ALL_PID_TYPE
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
        'publish_permission_factory_imp': deny_all,
        # Who can unpublish (delete published & create a new draft version of)
        # a published article record
        'unpublish_permission_factory_imp': deny_all,
        # Who can edit (create a new draft version of) a published dataset record
        'edit_permission_factory_imp': deny_all,
        # Who can enumerate published articles
        'list_permission_factory_imp': deny_all,
        # Who can view a detail of an existing published article
        'read_permission_factory_imp': deny_all,
        # Make sure everything else is for biden
        'create_permission_factory_imp': deny_all,
        'update_permission_factory_imp': deny_all,
        'delete_permission_factory_imp': deny_all,

        'default_media_type': 'application/json',
        'indexer_class': CommitingRecordIndexer,
        'search_index': 'oarepo-demo-s3-articles-publication-article-v1.0.0',
        'search_class': RecordsSearch,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },

        'list_route': '/publications/articles/',
        'files': dict(
            # File attachments are currently not allowed on article records
            put_file_factory=deny_all,
            get_file_factory=deny_all,
            delete_file_factory=deny_all
        )
    },
    'draft-publications/articles': {
        'pid_type': ARTICLE_DRAFT_PID_TYPE,
        'record_class': 'publications.articles.record.ArticleDraftRecord',
        'search_index': 'oarepo-demo-s3-draft-publication-article-v1.0.0',
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
            'application/json': 'oarepo_validate.json_files_loader'
        },
        'files': dict(
            # File attachments are currently not allowed on article records
            put_file_factory=deny_all,
            get_file_factory=deny_all,
            delete_file_factory=deny_all
        )
    }
}

RECORDS_REST_ENDPOINTS = {
    # readonly url for both endpoints, does not have item route
    # as it is accessed from the endpoints above
    'publications/all-articles': dict(
        pid_type=ARTICLE_ALL_PID_TYPE,
        pid_minter='all-publications-articles',
        pid_fetcher='all-publications-articles',
        default_endpoint_prefix=True,
        search_class=FilteredRecordsSearch,
        search_index='oarepo-demo-s3-all-articles',
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        list_route='/publications/all-articles/',
        default_media_type='application/json',
        max_result_window=10000,

        # not used really
        item_route='/publications/all-articles/not-used-but-must-be-present',
        create_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        read_permission_factory_imp=check_elasticsearch,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        search_factory_imp='publications.articles.search:article_search_factory'
    )
}
