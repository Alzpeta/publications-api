# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import datetime

from flask import url_for, current_app, jsonify
from flask_login import current_user
from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record
from jsonref import requests
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.endpoints import make_draft_minter
from oarepo_records_draft.record import DraftRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin, FilesKeepingRecordMixin
from oarepo_validate.record import AllowedSchemaMixin
from oarepo_actions.decorators import action
from publications.articles.search import MineRecordsSearch
from werkzeug.local import LocalProxy

from .constants import (
    ARTICLE_ALLOWED_SCHEMAS,
    ARTICLE_PREFERRED_SCHEMA, ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE
)
from .marshmallow import ArticleMetadataSchemaV1
from oarepo_documents.api import DocumentRecordMixin

class ArticleRecord(SchemaKeepingRecordMixin,
                    MarshmallowValidatedRecordMixin,
                    InheritedSchemaRecordMixin,
                    Record,
                    ):
    """Record class for an Article Record"""
    ALLOWED_SCHEMAS = ARTICLE_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = ARTICLE_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = ArticleMetadataSchemaV1

    #index_name = 'oarepo-demo-s3-articles-publication-article-v1.0.0'
    index_name = 'articles-publication-article-v1.0.0'
    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.publications/articles_item',
                       pid_value=self['id'], _external=True)


class ArticleDraftRecord(DocumentRecordMixin, DraftRecordMixin, ArticleRecord):
    DOCUMENT_MINTER = LocalProxy(lambda: make_draft_minter(ARTICLE_DRAFT_PID_TYPE,'publications-article'))
    DOCUMENT_INDEXER = RecordIndexer

    index_name = 'draft-articles-publication-article-v1.0.0'
    #index_name = 'oarepo-demo-s3-draft-articles-publication-article-v1.0.0'

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
                       pid_value=self['id'], _external=True)

class AllArticlesRecord(ArticleRecord):
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