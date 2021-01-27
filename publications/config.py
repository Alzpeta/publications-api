# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import os
from datetime import timedelta

from flask_babelex import lazy_gettext as _
from invenio_openid_connect import InvenioAuthOpenIdRemote

PIDSTORE_RECID_FIELD = 'id'
JSONSCHEMAS_HOST = 'repozitar.cesnet.cz'
SUPPORTED_LANGUAGES = ['cs', 'en', '_']

BABEL_DEFAULT_LOCALE = 'cs'
I18N_LANGUAGES = (('en', _('English')), ('cs', _('Czech')))
I18N_SESSION_KEY = 'language'
I18N_SET_LANGUAGE_URL = '/api/lang'

ELASTICSEARCH_DEFAULT_LANGUAGE_TEMPLATE = {
    "type": "text",
    "fields": {
        "raw": {
            "type": "keyword"
        }
    }
}

INDEXER_RECORD_TO_INDEX = 'publications.indexer:record_to_index'

# hack to serve schemas both on jsonschemas host and server name (if they differ)
import jsonresolver


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """JSON resolver plugin that loads the schema endpoint.

    Injected into Invenio-Records JSON resolver.
    """
    from flask import current_app
    from invenio_jsonschemas import current_jsonschemas
    from werkzeug.routing import Rule
    url_map.add(Rule(
        "{0}/<path:path>".format(current_app.config['JSONSCHEMAS_ENDPOINT']),
        endpoint=current_jsonschemas.get_schema,
        host=current_app.config['SERVER_NAME']))


FILES_REST_STORAGE_FACTORY = 'oarepo_s3.storage.s3_storage_factory'
CELERY_BEAT_SCHEDULE = {
    'cleanup_expired_multipart_uploads': {
        'task': 'oarepo_s3.tasks.cleanup_expired_multipart_uploads',
        'schedule': timedelta(minutes=60*24),
    }
}

REST_CSRF_ENABLED = False
CSRF_HEADER = 'X-CSRFTOKEN'
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
SESSION_COOKIE_PATH = '/'

OAISERVER_ID_PREFIX = 'oai:repozitar.cesnet.cz:'
MAIL_SUPPRESS_SEND = os.environ.get('FLASK_DEBUG', False)

OPENIDC_CONFIG = dict(
    base_url='https://login.cesnet.cz/oidc/',
    consumer_key=os.environ.get('OPENIDC_KEY', 'MISSING_OIDC_KEY'),
    consumer_secret=os.environ.get('OPENIDC_SECRET', 'MISSING_OIDC_SECRET'),
    scope='openid email profile'
)

OAUTHCLIENT_REST_REMOTE_APPS = dict(
    eduid=InvenioAuthOpenIdRemote().remote_app(),
)

