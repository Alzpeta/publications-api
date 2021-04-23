# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from oarepo_communities.marshmallow import OARepoCommunitiesMixin
from oarepo_fsm.marshmallow import FSMRecordSchemaMixin
from oarepo_rdm_records.marshmallow import DataSetMetadataSchemaV2


class PublicationDatasetMetadataSchemaV1(OARepoCommunitiesMixin,
                                         FSMRecordSchemaMixin,
                                         DataSetMetadataSchemaV2):
    """Schema for dataset drafts metadata."""
