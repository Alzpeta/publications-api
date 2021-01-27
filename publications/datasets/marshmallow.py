# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from oarepo_rdm_records.marshmallow import DataSetMetadataSchemaV1

from publications.marshmallow import check_multilingual_string_length


class PublicationDatasetMetadataSchemaV1(DataSetMetadataSchemaV1):
    """Schema for dataset drafts metadata."""

    @validates('abstract')
    def validate_abstract(self, val):
        if not check_multilingual_string_length(val['description'],
                                                max_words=self.context.get('max_words', 200),
                                                max_length=self.context.get('max_length', 5000)):
            raise ValidationError('Abstract must be under 200 words and 5000 characters.')
        else:
            return True
