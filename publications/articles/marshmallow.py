# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import fields, EXCLUDE, Schema
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin, InvenioRecordMetadataFilesMixin

from publications.marshmallow import check_multilingual_string_length
from oarepo_documents.marshmallow.document import DocumentSchemaV1


class ArticleMetadataSchemaV1(InvenioRecordMetadataFilesMixin,
                              InvenioRecordMetadataSchemaV1Mixin,
                              StrictKeysMixin,
                              DocumentSchemaV1):
    datasets = fields.List(fields.Str())


