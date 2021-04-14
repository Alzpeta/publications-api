# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import datetime
import os

from flask import url_for, jsonify, request
from flask_login import current_user
from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record
from oarepo_actions.decorators import action
from oarepo_communities.converters import CommunityPIDValue
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_communities.record import CommunityRecordMixin
from oarepo_documents.api import DocumentRecordMixin, getMetadataFromDOI
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.endpoints import make_draft_minter
from oarepo_records_draft.record import DraftRecordMixin, InvalidRecordAllowedMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin
from simplejson import JSONDecodeError
from werkzeug.local import LocalProxy

from publications.articles.search import MineRecordsSearch
from .constants import (
    ARTICLE_ALLOWED_SCHEMAS,
    ARTICLE_PREFERRED_SCHEMA, ARTICLE_DRAFT_PID_TYPE
)
from .marshmallow import ArticleMetadataSchemaV1

published_index_name = 'articles-publication-article-v1.0.0'
draft_index_name = 'draft-articles-publication-article-v1.0.0'
all_index_name = 'all-articles'

prefixed_published_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + published_index_name
prefixed_draft_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + draft_index_name
prefixed_all_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + all_index_name


class ArticleBaseRecord(SchemaKeepingRecordMixin,
                        MarshmallowValidatedRecordMixin,
                        InheritedSchemaRecordMixin,
                        CommunityRecordMixin,
                        Record):
    """Record class for an Article Record"""
    ALLOWED_SCHEMAS = ARTICLE_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = ARTICLE_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = ArticleMetadataSchemaV1


class ArticleRecord(InvalidRecordAllowedMixin, ArticleBaseRecord):
    index_name = published_index_name
    _schema = 'publication-article-v1.0.0.json'

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.publications/articles_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)
                       ), _external=True)


class ArticleDraftRecord(DocumentRecordMixin, DraftRecordMixin, ArticleBaseRecord):
    DOCUMENT_MINTER = LocalProxy(lambda: make_draft_minter(ARTICLE_DRAFT_PID_TYPE, 'publications-article'))
    DOCUMENT_INDEXER = RecordIndexer

    index_name = draft_index_name

    def validate(self, *args, **kwargs):
        if 'created' not in self:
            self['created'] = datetime.date.today().strftime('%Y-%m-%d')
        if 'creator' not in self:
            if current_user.is_authenticated:
                self['creator'] = current_user.email
            else:
                self['creator'] = 'anonymous'

        self['modified'] = datetime.date.today().strftime('%Y-%m-%d')
        return super().validate(*args, **kwargs)

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.draft-publications/articles_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)
                       ), _external=True)


class AllArticlesRecord(ArticleRecord):
    @classmethod
    @action(detail=False, url_path='from-doi/', method='post')
    def from_doi(cls, **kwargs):
        doi = request.json['doi']
        try:
            article = getMetadataFromDOI(doi)
        except(JSONDecodeError):
            return jsonify()

        if article is None:
            return jsonify()
        else:
            return jsonify(article=article)

    @classmethod
    @action(detail=False, url_path='mine')
    def my_records(cls, **kwargs):
        search = MineRecordsSearch(index='all-articles', doc_type='_doc')
        search = search.with_preference_param().params(version=True)
        search = search[0:10]
        search_result = search.execute().to_dict()
        search_result = {
            'hits': {
                'hits': [
                    x['_source'] for x in search_result['hits']['hits']
                ],
                'total': search_result['hits']['total']['value']
            },
        }

        return jsonify(search_result)
