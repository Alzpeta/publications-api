# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#


# DRAFT dataset record manipulation
from flask import request
from flask_principal import RoleNeed
from invenio_access import Permission
from invenio_records_rest.utils import deny_all
from oarepo_communities.api import OARepoCommunity
from oarepo_communities.permissions import read_object_permission_impl, create_object_permission_impl, \
    update_object_permission_impl, delete_object_permission_impl, publish_permission_impl, unpublish_permission_impl

from publications.permissions import ADMIN_ROLE_PERMISSIONS

create_draft_object_permission_impl = create_object_permission_impl
update_draft_object_permission_impl = update_object_permission_impl
read_draft_object_permission_impl = read_object_permission_impl
delete_draft_object_permission_impl = delete_object_permission_impl
list_draft_object_permission_impl = deny_all

# DRAFT dataset file manipulation
put_draft_file_permission_impl = update_object_permission_impl
delete_draft_file_permission_impl = update_object_permission_impl
get_draft_file_permission_impl = read_draft_object_permission_impl

# DRAFT dataset publishing
publish_draft_object_permission_impl = publish_permission_impl
unpublish_draft_object_permission_impl = unpublish_permission_impl

# PUBLISHED dataset manipulation
update_object_permission_impl = ADMIN_ROLE_PERMISSIONS


# ALL dataset list
def community_member_permission_impl(record, *args, **kwargs):
    community = OARepoCommunity.get_community(request.view_args['community_id'])
    return Permission(RoleNeed(OARepoCommunity.get_role(community, 'member').name))


list_all_object_permission_impl = community_member_permission_impl
