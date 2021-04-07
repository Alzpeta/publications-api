# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from publications.datasets import config


class PublicationsDatasets:
    def __init__(self, app=None, db=None):
        self.init_app(app, db)

    def init_app(self, app, db):
        self.init_config(app, db)

    def init_config(self, app, db):
        app.config.setdefault('RECORDS_DRAFT_ENDPOINTS', {}).update(
            config.RECORDS_DRAFT_ENDPOINTS
        )
        app.config.setdefault('RECORDS_REST_ENDPOINTS', {}).update(
            config.RECORDS_REST_ENDPOINTS
        )
        app.config.setdefault('RECORDS_REST_FACETS', {}).update(
            config.RECORDS_REST_FACETS
        )
        app.config.setdefault('RECORDS_REST_DEFAULT_SORT', {}).update(
            config.RECORDS_REST_DEFAULT_SORT
        )
        app.config.setdefault('RECORDS_REST_SORT_OPTIONS', {}).update(
            config.RECORDS_REST_SORT_OPTIONS
        )
