# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import logging
from flask import url_for
from oarepo_records_draft.proxies import current_drafts

log = logging.getLogger('dataset-minter')


def publications_links_factory(pid, record=None, **kwargs):
    if record:
        return dict(self=record.canonical_url)
    if pid:
        endpoint = current_drafts.endpoint_for_pid(pid).rest_name
        return dict(self=url_for(
            f'invenio_records_rest.{endpoint}_item',
            pid_value=pid.pid_value,
            _external=True
        ))
    return {}
