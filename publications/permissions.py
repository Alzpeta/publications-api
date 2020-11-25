# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_principal import Permission, RoleNeed, UserNeed
from invenio_access import authenticated_user


def allow_curator(*args, **kwargs):
    return Permission(
        RoleNeed('curator')
    )


def allow_authenticated(*args, **kwargs):
    return Permission(authenticated_user)


def allow_admin(*args, **kwargs):
    """Permissions factory for buckets."""
    return Permission(RoleNeed('admin'))


def allow_owner(record, *args, **kwargs):
    owners = record.get('_owners')
    return Permission(
        *[UserNeed(int(owner)) for owner in owners],
    )


def allow_ingester(record, *args, **kwargs):
    return Permission(RoleNeed('ingester'))


def allow_curator_or_owner(record, *args, **kwargs):
    owner = allow_owner(record, *args, **kwargs)
    curator = allow_curator(*args, **kwargs)
    return curator.union(owner)
