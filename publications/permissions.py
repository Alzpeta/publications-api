# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_principal import Permission, RoleNeed, UserNeed
from invenio_access import authenticated_user
from oarepo_fsm.permissions import require_any

CURATOR_ROLE_PERMISSIONS = Permission(
    RoleNeed('curator')
)

INGESTER_ROLE_PERMISSIONS = Permission(
    RoleNeed('ingester')
)

ADMIN_ROLE_PERMISSIONS = Permission(
    RoleNeed('admin')
)

AUTHENTICATED_PERMISSION = Permission(authenticated_user)


def owner_permission_impl(record, *args, **kwargs):
    owners = record.get('_owners')
    return Permission(
        *[UserNeed(int(owner)) for owner in owners],
    )


MODIFICATION_ROLE_PERMISSIONS = require_any(
    CURATOR_ROLE_PERMISSIONS,
    INGESTER_ROLE_PERMISSIONS,
    owner_permission_impl
)
PUBLISHER_ROLE_PERMISSION = CURATOR_ROLE_PERMISSIONS
DELETER_ROLE_PERMISSIONS = ADMIN_ROLE_PERMISSIONS



