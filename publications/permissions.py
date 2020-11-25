# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_principal import Permission, RoleNeed, UserNeed
from invenio_access import authenticated_user


def _get_owners(record):
    owners = record.get('_owners')
    try:
        owners.remove(-1)
    except ValueError:
        pass
    return owners


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
    owners = _get_owners(record)
    return Permission(
        *[UserNeed(int(owner)) for owner in owners],
        Permission(UserNeed(-1))
    )


def allow_curator_or_owner(record, *args, **kwargs):
    owner = allow_owner(record, *args, **kwargs)
    curator = allow_curator(*args, **kwargs)
    return curator.union(owner)
