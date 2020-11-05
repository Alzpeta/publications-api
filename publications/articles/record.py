# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import datetime

from flask import url_for
from flask_login import current_user
from invenio_records_files.api import Record
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.record import DraftRecordMixin
from oarepo_references.mixins import ReferenceEnabledRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin, FilesKeepingRecordMixin
from oarepo_validate.record import AllowedSchemaMixin

from .constants import (
    ARTICLE_ALLOWED_SCHEMAS,
    ARTICLE_PREFERRED_SCHEMA, ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE
)
from .marshmallow import ArticleMetadataSchemaV1


class ArticleRecord(SchemaKeepingRecordMixin,
                    MarshmallowValidatedRecordMixin,
                    InheritedSchemaRecordMixin,
                    ReferenceEnabledRecordMixin,
                    Record):
    """Record class for an Article Record"""
    ALLOWED_SCHEMAS = ARTICLE_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = ARTICLE_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = ArticleMetadataSchemaV1

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.publications/{ARTICLE_PID_TYPE}_item',
                       pid_value=self['id'], _external=True)


class ArticleDraftRecord(DraftRecordMixin, ArticleRecord):
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
        return url_for(f'invenio_records_rest.draft-publications/{ARTICLE_DRAFT_PID_TYPE}_item',
                       pid_value=self['id'], _external=True)
