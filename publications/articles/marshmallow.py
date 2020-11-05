# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin, InvenioRecordMetadataFilesMixin

from publications.marshmallow import check_multilingual_string_length


# TODO: inherit from oarepo-documents
class ArticleMetadataSchemaV1(InvenioRecordMetadataFilesMixin,
                              InvenioRecordMetadataSchemaV1Mixin,
                              StrictKeysMixin):

    @validates('abstract')
    def validate_description(self, val):
        if not check_multilingual_string_length(val, max_words=self.context.get('max_words', 200)):
            raise ValidationError('Abstract must be under 200 words.')
        else:
            return True
