# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#


# DRAFT dataset record manipulation
from oarepo_fsm.permissions import require_any
from oarepo_communities.permissions import read_object_permission_impl
from publications.permissions import MODIFICATION_ROLE_PERMISSIONS, AUTHENTICATED_PERMISSION, DELETER_ROLE_PERMISSIONS, \
    ADMIN_ROLE_PERMISSIONS

create_draft_object_permission_impl = require_any(
    MODIFICATION_ROLE_PERMISSIONS,
    AUTHENTICATED_PERMISSION
)
update_draft_object_permission_impl = MODIFICATION_ROLE_PERMISSIONS
read_draft_object_permission_impl = read_object_permission_impl
delete_draft_object_permission_impl = DELETER_ROLE_PERMISSIONS
list_draft_object_permission_impl = AUTHENTICATED_PERMISSION

# DRAFT dataset file manipulation
put_draft_file_permission_impl = update_draft_object_permission_impl
delete_draft_file_permission_impl = update_draft_object_permission_impl
get_draft_file_permission_impl = update_draft_object_permission_impl

# DRAFT dataset publishing
publish_draft_object_permission_impl = MODIFICATION_ROLE_PERMISSIONS
unpublish_draft_object_permission_impl = MODIFICATION_ROLE_PERMISSIONS

# PUBLISHED dataset manipulation
update_object_permission_impl = ADMIN_ROLE_PERMISSIONS
