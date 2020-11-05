# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import logging
import uuid

from flask_login import current_user
from invenio_pidstore.errors import PIDDoesNotExistError

from publications.datasets.constants import DATASET_PID_TYPE
from publications.providers import PublicationProvider


log = logging.getLogger('dataset-minter')


class DatasetProvider(PublicationProvider):
    pid_type = DATASET_PID_TYPE


def dataset_minter(record_uuid, data):
    provider = None

    if 'id' not in data:
        data['identifier'] = data['id'] = str(uuid.uuid4())
        provider = DatasetProvider.create(
            object_type='rec',
            object_uuid=record_uuid,
            pid_value=data['id'],
        )
    else:
        try:
            provider = DatasetProvider.get(pid_value=str(data['id']))
        except PIDDoesNotExistError:
            if current_user.has_role('synchronizer'):
                provider = DatasetProvider.create(
                    object_type='rec',
                    object_uuid=record_uuid,
                    pid_value=data['id'],
                )
                return provider.pid
            else:
                log.error('Id present in data but user has no role `synchronizer` - bailing out')
            raise

    return provider.pid


def dataset_all_minter(record_uuid, data):
    raise Exception('Should not be used as all datasets are readonly for all view')
