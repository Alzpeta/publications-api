# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_principal import Permission, RoleNeed
from invenio_access import authenticated_user

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
