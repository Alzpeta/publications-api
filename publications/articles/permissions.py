# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_records_rest.utils import deny_all
from oarepo_communities.permissions import create_object_permission_impl, read_object_permission_impl, \
    delete_object_permission_impl, publish_permission_impl, unpublish_permission_impl, update_object_permission_impl

from publications.permissions import ADMIN_ROLE_PERMISSIONS

create_draft_object_permission_impl = create_object_permission_impl
update_draft_object_permission_impl = update_object_permission_impl
read_draft_object_permission_impl = read_object_permission_impl
delete_draft_object_permission_impl = delete_object_permission_impl
list_draft_object_permission_impl = deny_all

# DRAFT artic file manipulation
put_draft_file_permission_impl = update_object_permission_impl
delete_draft_file_permission_impl = update_object_permission_impl
get_draft_file_permission_impl = read_draft_object_permission_impl

# DRAFT dataset publishing
publish_draft_object_permission_impl = publish_permission_impl
unpublish_draft_object_permission_impl = unpublish_permission_impl

# PUBLISHED dataset manipulation
update_object_permission_impl = ADMIN_ROLE_PERMISSIONS
