# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_records_rest.serializers import record_responsify
from oarepo_validate import JSONSerializer as BaseSerializer

from publications.datasets.permissions import update_draft_object_permission_impl


class JSONSerializer(BaseSerializer):
    def transform_record(self, pid, record, *args, **kwargs):
        """Transform record into an intermediate representation."""
        ret = super().transform_record(pid, record, *args, **kwargs)
        ret['permissions'] = {
            'update': update_draft_object_permission_impl(record=record).can(),
            'delete': False,
        }
        return ret


json_serializer = JSONSerializer(replace_refs=False)

json_response = record_responsify(json_serializer, 'application/json')
