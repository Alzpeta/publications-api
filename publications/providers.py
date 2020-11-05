# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.base import BaseProvider


class PublicationProvider(BaseProvider):
    pid_type = None
    pid_provider = None

    default_status = PIDStatus.REGISTERED

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        assert 'pid_value' in kwargs
        kwargs.setdefault('status', cls.default_status)
        return super().create(
            object_type=object_type, object_uuid=object_uuid, **kwargs)
