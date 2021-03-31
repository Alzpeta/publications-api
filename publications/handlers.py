# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import traceback

from flask import make_response, jsonify
from flask_restful import abort
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from oarepo_communities.links import community_record_links_factory
from oarepo_records_draft import current_drafts
from oarepo_records_draft.exceptions import InvalidRecordException

from publications.datasets.constants import DATASET_DRAFT_PID_TYPE
from publications.datasets.record import DatasetDraftRecord


def handle_request_approval(sender, **kwargs):
    if isinstance(sender, DatasetDraftRecord):
        print('request draft dataset approval', sender)
        # TODO: send mail notification to community curators


def handle_request_changes(sender, **kwargs):
    if isinstance(sender, DatasetDraftRecord):
        print('requesting changes for draft dataset', sender)
        # TODO: send mail notification to record owner


def handle_approve(sender, force=False, **kwargs):
    if isinstance(sender, DatasetDraftRecord):
        print('approving draft dataset', sender)
        record_pid = PersistentIdentifier.query. \
            filter_by(pid_type=DATASET_DRAFT_PID_TYPE, object_uuid=sender.id).one()
        try:
            published = \
                current_drafts.publish(sender, record_pid, require_valid=not force)
            db.session.commit()

            # TODO: (mirekys,mesemus) fix bug in default_links_factory picking wrong endpoint for pid_type
            links = community_record_links_factory(pid=published[0].published_context.record_pid,
                                                   record=published[0].published_context.record)

            return {
                'url': links['self'],
                'pid_type': published[0].published_context.record_pid.pid_type,
                'pid': published[0].published_context.record_pid.pid_value,
            }
        except InvalidRecordException as e:
            traceback.print_exc()
            abort(make_response(jsonify({
                "status": "error",
                "message": e.message,
                "errors": e.errors
            }), 400))
        except:
            traceback.print_exc()
            raise

