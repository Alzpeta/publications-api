# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import absolute_import, print_function

import logging

from flask_login import current_user
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2

from publications.articles.constants import ARTICLE_PID_TYPE

log = logging.getLogger('article-minter')


class ArticleProvider(RecordIdProviderV2):
    pid_type = ARTICLE_PID_TYPE
    """Type of persistent identifier."""

    @classmethod
    def generate_id(cls, options=None):
        """Generate record id."""

        return 'art-' + super().generate_id(options)


class DOINotInData(Exception):
    def __init__(self, message="DOI not found in data"):
        self.message = message
        super().__init__(self.message)


def getDoi(data):
    alt_id = data['alternative_identifiers']
    doi = ''
    for id in alt_id:
        if id['scheme'] == 'DOI':
            doi = id['value']
    if (doi != ''):
        return doi
    else:
        raise DOINotInData


def article_minter(record_uuid, data):
    if 'id' not in data:
        data['id'] = RecordIdProviderV2.generate_id()
        # todo ArticleProvider podedit od RecordIdProviderV2
        doi = getDoi(data)
        print(doi)
        PersistentIdentifier.create('doi', doi, object_type='rec',
                                    object_uuid=record_uuid,
                                    status=PIDStatus.REGISTERED)

        provider = ArticleProvider.create(
            object_type='rec',
            object_uuid=record_uuid,
            pid_value=data['id']
        )
    else:
        try:
            provider = ArticleProvider.get(pid_value=str(data['id']))
        except PIDDoesNotExistError:
            if current_user.has_role('synchronizer'):
                provider = ArticleProvider.create(
                    object_type='rec',
                    object_uuid=record_uuid,
                    pid_value=data['id'],
                )
                return provider.pid
            else:
                log.error('Id present in data but user has no role `synchronizer` - bailing out')
            raise
    return provider.pid


def article_all_minter(record_uuid, data):
    raise Exception('Should not be used as all datasets are readonly for all view')


# temporary solution todo: delete this
def article_minter_withoutdoi(record_uuid, data):
    if 'id' not in data:
        data['id'] = RecordIdProviderV2.generate_id()
        # todo ArticleProvider podedit od RecordIdProviderV2
        provider = ArticleProvider.create(
            object_type='rec',
            object_uuid=record_uuid,
            pid_value=data['id']
        )
    else:
        try:
            provider = ArticleProvider.get(pid_value=str(data['id']))
        except PIDDoesNotExistError:
            if current_user.has_role('synchronizer'):
                provider = ArticleProvider.create(
                    object_type='rec',
                    object_uuid=record_uuid,
                    pid_value=data['id'],
                )
                return provider.pid
            else:
                log.error('Id present in data but user has no role `synchronizer` - bailing out')
            raise

    return provider.pid
