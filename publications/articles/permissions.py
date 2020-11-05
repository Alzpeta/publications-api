# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from flask_principal import Permission, RoleNeed


def create_work_permission_impl(*args, **kwargs):
    return Permission(
        RoleNeed('synchronizer'),
        RoleNeed('curator'),
    )


def update_work_permission_impl(*args, **kwargs):
    return Permission(
        RoleNeed('synchronizer'),
        RoleNeed('curator'),
    )


def put_file_permission_impl(*args, **kwargs):
    return Permission(
        RoleNeed('synchronizer'),
        RoleNeed('curator'),
    )


def get_file_permission_impl(*args, **kwargs):
    return Permission(
        RoleNeed('synchronizer'),
        RoleNeed('curator'),
    )
