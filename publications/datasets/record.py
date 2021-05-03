# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import datetime
import os

from flask import url_for
from flask_login import current_user
from invenio_records_files.api import Record
from oarepo_communities.converters import CommunityPIDValue
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_communities.record import CommunityRecordMixin
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.record import DraftRecordMixin, InvalidRecordAllowedMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin, FilesKeepingRecordMixin

from publications.datasets.constants import DATASET_ALLOWED_SCHEMAS, \
    DATASET_PREFERRED_SCHEMA
from publications.datasets.marshmallow import PublicationDatasetMetadataSchemaV1

published_index_name = 'datasets-publication-dataset-v1.0.0'
draft_index_name = 'draft-datasets-publication-dataset-v1.0.0'
all_index_name = 'all-datasets'

prefixed_published_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + published_index_name
prefixed_draft_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + draft_index_name
prefixed_all_index_name = os.environ.get('INVENIO_SEARCH_INDEX_PREFIX', '') + all_index_name


class DatasetBaseRecord(SchemaKeepingRecordMixin,
                        MarshmallowValidatedRecordMixin,
                        InheritedSchemaRecordMixin,
                        CommunityRecordMixin,
                        Record):
    """Base Data set record class for Data set records."""
    ALLOWED_SCHEMAS = DATASET_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASET_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = PublicationDatasetMetadataSchemaV1


class DatasetRecord(InvalidRecordAllowedMixin, DatasetBaseRecord):
    index_name = published_index_name
    _schema = 'publication-dataset-v1.0.0.json'

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.datasets_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)
                       ), _external=True)


class DatasetDraftRecord(DraftRecordMixin,
                         FilesKeepingRecordMixin,
                         DatasetBaseRecord):
    index_name = draft_index_name

    @property
    def canonical_url(self):
        return url_for(f'invenio_records_rest.draft-datasets_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)
                       ), _external=True)


class AllDatasetsRecord(DatasetRecord):
    index_name = all_index_name
