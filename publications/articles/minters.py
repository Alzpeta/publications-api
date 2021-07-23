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

        return  super().generate_id(options)


def get_doi(data):
    # TODO: make consistent with article jsonschema identifiers field
    alt_ids = data.get('alternative_identifiers', [])
    doi = None
    for idf in alt_ids:
        # Return the first DOI we find in identifiers field
        if idf['scheme'] == 'DOI':
            doi = idf['value']
            break

    return doi


def article_minter(record_uuid, data):
    """Similar to Dataset minter, but also creates DOI PIDs for articles."""
    assert 'id' not in data

    doi = get_doi(data)
    doi_ids = [d.value for d in data.get('identifiers', []) if d.scheme == 'doi']

    if doi and doi not in doi_ids:
        # Append DOI to additional article identifiers metadata field
        data.setdefault('identifiers', []).append({
            'scheme': 'doi',
            'value': doi
        })
        # And persist DOI PID reference to record in database
        PersistentIdentifier.create('doi', doi, object_type='rec',
                                    object_uuid=record_uuid,
                                    status=PIDStatus.REGISTERED)

    provider = ArticleProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    data['id'] = provider.pid.pid_value
    return provider.pid


def article_all_minter(record_uuid, data):
    raise Exception('Should not be used as all datasets are readonly for all view')
