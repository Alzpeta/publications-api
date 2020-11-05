# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from types import SimpleNamespace

from flask import request
from invenio_base.utils import obj_or_import_string
from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record
from invenio_records_files.api import FileObject
from invenio_records_rest.views import verify_record_permission
from invenio_search import RecordsSearch
from oarepo_records_draft import current_drafts


def get_file_object(uuid):
    uuid = uuid[4:]
    pid_type, pid_value, key = uuid.split(':', maxsplit=2)
    pid = PersistentIdentifier.get(pid_type, pid_value)
    endpoint = current_drafts.endpoint_for_pid_type(pid_type)
    permission_factory = obj_or_import_string(endpoint.rest['read_permission_factory_imp'])
    record = endpoint.record_class.get_record(pid.object_uuid)
    request._methodview = SimpleNamespace(
        search_class=obj_or_import_string(endpoint.rest.get('search_class', RecordsSearch))
    )
    verify_record_permission(permission_factory, record)
    return record.files[key]


def checker(uuid, app=None, **kwargs):
    if not uuid.startswith('img:'):
        return False
    # get the file object - this evaluates permissions
    get_file_object(uuid)
    return True


def opener(uuid, app=None, **kwargs):
    if not uuid.startswith('img:'):
        return False
    # get the file object - this evaluates permissions
    f = get_file_object(uuid)
    obj = f.get_version(f['version_id'])
    return obj.file.storage().open('rb')


def identifier_maker(record: Record, file: FileObject, pid: PersistentIdentifier, app=None, **kwargs):
    try:
        mimetype = file['mime_type']
        if not mimetype.startswith('image/'):
            return None
        return f'img:{pid.pid_type}:{pid.pid_value}:{file["key"]}'
    except KeyError:
        return None
