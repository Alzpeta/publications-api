# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from oarepo_communities.constants import STATE_PUBLISHED, PRIMARY_COMMUNITY_FIELD, SECONDARY_COMMUNITY_FIELD, \
    STATE_APPROVED
from oarepo_communities.search import CommunitySearch

from publications.permissions import COMMUNITY_MEMBER_PERMISSION, AUTHENTICATED_PERMISSION, COMMUNITY_CURATOR_PERMISSION


class DatasetRecordsSearch(CommunitySearch):
    """Dataset collection search."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._source = [
            'id', 'oarepo:validity.valid', 'oarepo:draft', 'titles', 'created',
            'abstract', 'state', PRIMARY_COMMUNITY_FIELD, SECONDARY_COMMUNITY_FIELD]
        self._highlight['titles.cs'] = {}
        self._highlight['titles._'] = {}
        self._highlight['titles.en'] = {}

    class Meta:
        doc_types = ['_doc']
        default_anonymous_filter = Q('term', state=STATE_PUBLISHED)
        default_authenticated_filter = Q('terms', state=[STATE_APPROVED, STATE_PUBLISHED])

        @staticmethod
        def default_filter_factory(search=None, **kwargs):
            if not AUTHENTICATED_PERMISSION.can() or not COMMUNITY_MEMBER_PERMISSION(None).can():
                # Anonymous or non-community members sees published community records only
                return Bool(must=[
                    DatasetRecordsSearch.Meta.default_anonymous_filter,
                    CommunitySearch.community_filter()])
            else:
                if COMMUNITY_CURATOR_PERMISSION(None).can():
                    # Curators can see all community records
                    return CommunitySearch.community_filter()

                # Community member sees both APPROVED and PUBLISHED community records only
                q = Bool(must=[
                    CommunitySearch.community_filter(),
                    DatasetRecordsSearch.Meta.default_authenticated_filter])

                # TODO(mirekys): implement owned records filter
            return q


class MineRecordsSearch(DatasetRecordsSearch):
    class Meta:
        doc_types = ['_doc']
        facets = {}
        default_anonymous_filter = Q('match_none')

        @staticmethod
        def default_filter_factory(search=None, **kwargs):
            return MineRecordsSearch.Meta.default_anonymous_filter
