# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from invenio_records_rest.query import default_search_factory


def dataset_search_factory(self, search, query_parser=None):
    search, kwargs = default_search_factory(self, search, query_parser)
    search = search.source(['id', 'oarepo:validity.valid', 'title', 'created',
                            'articles.creator', 'description'])
    search = search.highlight('*')
    return search, kwargs