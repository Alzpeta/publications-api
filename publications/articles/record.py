# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import datetime
import uuid

from flask import url_for, jsonify, request, Response
from flask_login import current_user
from invenio_accounts.utils import obj_or_import_string
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record
from oarepo_documents.document_json_mapping import schema_mapping
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.endpoints import make_draft_minter
from oarepo_records_draft.record import DraftRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin
from oarepo_actions.decorators import action
from simplejson import JSONDecodeError

from publications.articles.search import MineRecordsSearch
from werkzeug.local import LocalProxy

from . import minters
from .constants import (
    ARTICLE_ALLOWED_SCHEMAS,
    ARTICLE_PREFERRED_SCHEMA, ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE
)
from .marshmallow import ArticleMetadataSchemaV1
from oarepo_documents.api import DocumentRecordMixin, getMetadataFromDOI, create_document


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
    @classmethod
    @action(detail=False, url_path='from-doi/', method='post')
    def from_doi(cls, **kwargs):
        doi = request.json['doi']
        try:
            pid = PersistentIdentifier.get('doi', doi)
            record = cls.get_record(pid.object_uuid)

            return Response(status=302, headers={"Location": record.canonical_url})
        except PIDDoesNotExistError:
            pass
        try:
            existing_document = getMetadataFromDOI(doi)
            article = schema_mapping(existing_record=existing_document, doi=doi)
        except(JSONDecodeError):
            return jsonify()

        if article is None:
            return jsonify()
        else:
            return jsonify(article=article)

    @classmethod
    @action(detail=False, url_path='create_article/', method='post')
    def create_article(cls, **kwargs):
        changes = request.json['changes']
        authors = request.json['authors']
        generated_article = request.json['generated_article']
        article = data_to_article(changes,generated_article, authors)
        create_document(cls, article, changes['doi'])

    #temporary solution todo: delet this and create own doi
    @classmethod
    @action(detail=False, url_path='without_doi/', method='post')
    def without_doi(cls, **kwargs):
        changes = request.json['changes']
        authors = request.json['authors']
        generated_article = request.json['generated_article']
        article = data_to_article(changes, generated_article, authors)
        record_uuid = uuid.uuid4()
        minter = cls.DOCUMENT_MINTER
        if hasattr(minter, '_get_current_object'):
            minter = minter._get_current_object()
        if isinstance(minter, str):
            minter = obj_or_import_string(current_pidstore.minters[minter])
        pid = minter(record_uuid, article)
        record = cls.create(data=article, id_=record_uuid)
        indexer = cls.DOCUMENT_INDEXER()
        indexer.index(record)

        PersistentIdentifier.create(cls.DOI_PID_TYPE, pid.pid_value, object_type='rec',
                                    object_uuid=record_uuid,
                                    status=PIDStatus.REGISTERED)
        db.session.commit()
        return Response(status=302, headers={"Location": record.canonical_url})



    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.draft-publications/articles_item',
                       pid_value=self['id'], _external=True)

class AllArticlesRecord(ArticleRecord):
    @classmethod
    @action(detail=False, url_path='from-doi/', method='post')
    def from_doi(cls, **kwargs):
        doi = request.json['doi']
        try:
            pid = PersistentIdentifier.get('doi', doi)
            record = cls.get_record(pid.object_uuid)

            return Response(status=302, headers={"Location": record.canonical_url})
        except PIDDoesNotExistError:
            pass
        try:
            existing_document = getMetadataFromDOI(doi)
            article = schema_mapping(existing_record=existing_document, doi=doi)
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

def data_to_article(data, article, authors):
    article['title'] = {data['title_lang'] : data['title_val']}
    article['abstract'] = {data['abstract_lang']: data['abstract_val']}
    article['authors'] = authors
    article['document_type'] = data['document_type']
    return article