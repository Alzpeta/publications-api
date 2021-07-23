# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_principal import Permission, RoleNeed
from invenio_access import authenticated_user
from oarepo_communities.permissions import community_member_permission_impl, community_curator_permission_impl, \
    community_publisher_permission_impl

INGESTER_ROLE_PERMISSIONS = Permission(
    RoleNeed('ingester')
)

ADMIN_ROLE_PERMISSIONS = Permission(
    RoleNeed('admin')
)

AUTHENTICATED_PERMISSION = Permission(authenticated_user)

# Community permissions
COMMUNITY_MEMBER_PERMISSION = community_member_permission_impl
COMMUNITY_CURATOR_PERMISSION = community_curator_permission_impl
COMMUNITY_PUBLISHER_PERMISSION = community_publisher_permission_impl
