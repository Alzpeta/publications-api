# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from oarepo_communities.signals import on_request_approval, on_request_changes, on_approve

from publications.handlers import handle_request_approval, handle_request_changes, handle_approve


class Publications:
    def __init__(self, app=None, db=None):
        self.init_app(app, db)

    def init_app(self, app, db):
        self.connect_signals(app)

    def connect_signals(self, app):
        on_request_approval.connect(handle_request_approval)
        on_request_changes.connect(handle_request_changes)
        on_approve.connect(handle_approve)
