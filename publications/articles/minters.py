# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import absolute_import, print_function

import uuid

from flask_login import current_user
from invenio_pidstore.errors import PIDDoesNotExistError

from publications.articles.constants import ARTICLE_PID_TYPE
from publications.providers import PublicationProvider
import logging

log = logging.getLogger('article-minter')


class ArticleProvider(PublicationProvider):
    pid_type = ARTICLE_PID_TYPE
    """Type of persistent identifier."""


def article_minter(record_uuid, data):
    if 'id' not in data:
        data['id'] = str(uuid.uuid4())
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
