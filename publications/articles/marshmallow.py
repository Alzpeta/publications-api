# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import fields, Schema, validates, ValidationError
from marshmallow_utils.fields import SanitizedUnicode
from oarepo_communities.marshmallow import OARepoCommunitiesMixin
from oarepo_documents.marshmallow.document import DocumentSchemaV1
from oarepo_fsm.marshmallow import FSMRecordSchemaMixin
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin


class NestedDatasetMetadataSchemaV1(Schema):
    pid_value = SanitizedUnicode()
    _oarepo_draft = fields.Boolean(attribute='oarepo:draft')


class ArticleMetadataSchemaV1(InvenioRecordMetadataSchemaV1Mixin,
                              OARepoCommunitiesMixin,
                              FSMRecordSchemaMixin,
                              StrictKeysMixin,
                              DocumentSchemaV1):
    datasets = fields.List(fields.Nested(NestedDatasetMetadataSchemaV1), default=list)

    @validates('datasets')
    def validate_datasets(self, val):
        orig_len = len(val)
        unique_len = len(set(val for dic in val for val in dic.values()))
        if orig_len != unique_len:
            raise ValidationError('Datasets list contains duplicit references.')
