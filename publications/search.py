# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from elasticsearch_dsl import Q
from flask_login import current_user
from invenio_search import RecordsSearch
from invenio_search.api import DefaultFilter


def search_permission_filter():
    """Search returning only owned records."""
    if current_user.is_authenticated:
        if 'curator' in [rol.name for rol in current_user.roles]:
            # Curators can see the whole search index
            return Q('match_all')
        return Q('terms', _owners=current_user.get_id())
    return Q('match_none')


class FilteredRecordsSearch(RecordsSearch):
    class Meta:
        doc_types = None
        default_filter = DefaultFilter(search_permission_filter)
