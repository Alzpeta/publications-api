# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import datetime

from flask import url_for, current_app
from flask_login import current_user
from invenio_records_files.api import Record
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.record import DraftRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin, FilesKeepingRecordMixin
from oarepo_validate.record import AllowedSchemaMixin

from publications.datasets.constants import DATASET_ALLOWED_SCHEMAS,\
    DATASET_PREFERRED_SCHEMA, DATASET_PID_TYPE, DATASET_DRAFT_PID_TYPE
from publications.datasets.marshmallow import DatasetMetadataSchemaV1


class DatasetRecord(SchemaKeepingRecordMixin,
                    MarshmallowValidatedRecordMixin,
                    InheritedSchemaRecordMixin,
                    Record):
    """Data set record class for Data set records."""
    ALLOWED_SCHEMAS = DATASET_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASET_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = DatasetMetadataSchemaV1

    index_name = 'oarepo-demo-s3-datasets-publication-dataset-v1.0.0'
    _schema = 'publication-dataset-v1.0.0.json'

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.publications/{DATASET_PID_TYPE}_item',
                       pid_value=self['id'], _external=True)


class DatasetDraftRecord(DraftRecordMixin,
                         FilesKeepingRecordMixin,
                         DatasetRecord):

    index_name = 'oarepo-demo-s3-draft-datasets-publication-dataset-v1.0.0'

    def validate(self, *args, **kwargs):
        if 'created' not in self:
            self['created'] = datetime.date.today().strftime('%Y-%m-%d')
        if 'creator' not in self:
            if current_user and current_user.is_authenticated:
                self['creator'] = current_user.email
            else:
                self['creator'] = 'anonymous'

        self['modified'] = datetime.date.today().strftime('%Y-%m-%d')
        return super().validate(*args, **kwargs)

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.draft-publications/{DATASET_DRAFT_PID_TYPE}_item',
                       pid_value=self['id'], _external=True)
