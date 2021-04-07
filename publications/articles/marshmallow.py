# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import fields
from oarepo_communities.marshmallow import OARepoCommunitiesMixin
from oarepo_documents.marshmallow.document import DocumentSchemaV1
from oarepo_fsm.marshmallow import FSMRecordSchemaMixin
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin


class ArticleMetadataSchemaV1(InvenioRecordMetadataSchemaV1Mixin,
                              OARepoCommunitiesMixin,
                              FSMRecordSchemaMixin,
                              StrictKeysMixin,
                              DocumentSchemaV1):
    datasets = fields.List(fields.Str())
