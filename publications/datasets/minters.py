# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import logging

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2

from publications.datasets.constants import DATASET_PID_TYPE

log = logging.getLogger('dataset-minter')


class DatasetProvider(RecordIdProviderV2):
    pid_type = DATASET_PID_TYPE

    @classmethod
    def generate_id(cls, options=None):
        """Generate record id."""
        
        return 'dat-' + super().generate_id(options)


def dataset_minter(record_uuid, data):
    assert 'id' not in data
    provider = DatasetProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    data['id'] = provider.pid.pid_value
    return provider.pid


def dataset_all_minter(record_uuid, data):
    raise Exception('Should not be used as all datasets are readonly for all view')
