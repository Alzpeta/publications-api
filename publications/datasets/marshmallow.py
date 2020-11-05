# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin, InvenioRecordMetadataFilesMixin
from oarepo_rdm_records.marshmallow import MetadataSchemaV1

from publications.marshmallow import check_multilingual_string_length


class DatasetMetadataSchemaV1(
    InvenioRecordMetadataFilesMixin,
    InvenioRecordMetadataSchemaV1Mixin,
    MetadataSchemaV1,
    StrictKeysMixin):
    """Schema for dataset drafts metadata."""

    @validates('description')
    def validate_description(self, val):
        if not check_multilingual_string_length(val,
                                                max_words=self.context.get('max_words', 200),
                                                max_length=self.context.get('max_length', 5000)):
            raise ValidationError('Description must be under 200 words and 5000 characters.')
        else:
            return True
