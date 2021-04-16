# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import datetime
import os
import uuid

from deepmerge import always_merger
from flask import url_for, jsonify, request, Response, abort
from flask_login import current_user
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError, PIDDeletedError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record
from oarepo_actions.decorators import action
from oarepo_communities.converters import CommunityPIDValue
from oarepo_communities.permissions import read_permission_factory
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_communities.record import CommunityRecordMixin
from oarepo_communities.views import json_abort
from oarepo_documents.api import getMetadataFromDOI
from oarepo_documents.document_json_mapping import schema_mapping
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft import current_drafts
from oarepo_records_draft.record import DraftRecordMixin, InvalidRecordAllowedMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin
from simplejson import JSONDecodeError

from .constants import (
    ARTICLE_ALLOWED_SCHEMAS,
    ARTICLE_PREFERRED_SCHEMA
)
from .marshmallow import ArticleMetadataSchemaV1
from .minters import article_minter_withoutdoi
from .permissions import create_draft_object_permission_impl

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


class DOIRecordMixin:
    DOI_PID_TYPE = 'doi'

    @classmethod
    @action(detail=False, url_path='from-doi/', method='post',
            permissions=create_draft_object_permission_impl)
    def from_doi(cls, **kwargs):
        """Returns an existing article record metadata by its DOI PID.

            If no record is found, tries to resolve article metadata from
            DOI using CrossRef client.
        """
        doi = request.json['doi']
        doi_pid = None

        try:
            doi_pid = PersistentIdentifier.get(cls.DOI_PID_TYPE, doi)
        except PIDDoesNotExistError:
            pass
        except PIDDeletedError:
            pass

        if doi_pid:
            # Found existing article record with this DOI
            record = cls.get_record(doi_pid.object_uuid)

            # Check if user has permission to read the article
            if not read_permission_factory(record).can():
                from flask_login import current_user
                if not current_user.is_authenticated:
                    abort(401)
                abort(403)

            # Get REST endpoint config and Invenio PID for the record
            endpoint = current_drafts.endpoint_for_record(record)
            pid_type = endpoint.pid_type
            pid_value = record.model.json['id']
            primary_pid = PersistentIdentifier.get(pid_type, pid_value)
            links_factory_imp = endpoint.rest.get('links_factory_imp')

            links = {}
            if links_factory_imp:
                links = links_factory_imp(primary_pid, record)

            return jsonify(dict(
                article=record.dumps(),
                links=links
            ))
        else:
            # Try to resolve record metadata from DOI with CrossRef
            metadata = None
            try:
                resolved_document = getMetadataFromDOI(doi)
                metadata = schema_mapping(existing_record=resolved_document, doi=doi)
                metadata['datasets'] = []
            except JSONDecodeError as e:
                json_abort(404, 'DOI could not be resolved: %s' % e)
            
            if metadata:
                return jsonify(dict(article=metadata))

            json_abort(404, 'Article not found by given DOI.')


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


class ArticleDraftRecord(DraftRecordMixin, DOIRecordMixin, ArticleBaseRecord):
    index_name = draft_index_name

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.draft-publications/articles_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)
                       ), _external=True)

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

    # temporary solution todo: delet this and create own doi
    @classmethod
    @action(detail=False, url_path='without_doi/', method='post')
    def without_doi(cls, **kwargs):
        changes = request.json['changes']
        authors = request.json['authors']
        datasetUrl = request.json['datasetUrl']
        article = {}
        article['title'] = {changes['title_lang']: changes['title_val']}
        article['abstract'] = {changes['abstract_lang']: changes['abstract_val']}
        article['authors'] = authors
        article['document_type'] = changes['document_type']
        always_merger.merge(article, {
            "_primary_community": 'cesnet',
            "access_right_category": "success"
        })
        article['datasets'] = [datasetUrl]
        print(article)
        record_uuid = uuid.uuid4()
        pid = article_minter_withoutdoi(record_uuid, article)
        record = cls.create(data=article, id_=record_uuid)
        indexer = cls.DOCUMENT_INDEXER()
        indexer.index(record)

        PersistentIdentifier.create('dpsart', pid.pid_value, object_type='rec',
                                    object_uuid=record_uuid,
                                    status=PIDStatus.REGISTERED)
        db.session.commit()
        return Response(status=302, headers={"Location": record.canonical_url})


class AllArticlesRecord(DOIRecordMixin, ArticleRecord):
    index_name = all_index_name
