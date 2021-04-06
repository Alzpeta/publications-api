# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import traceback
from typing import List

from flask import make_response, jsonify
from flask_restful import abort
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from oarepo_records_draft import current_drafts
from oarepo_records_draft.exceptions import InvalidRecordException
from oarepo_records_draft.ext import PublishedDraftRecordPair

from publications.datasets.constants import DATASET_DRAFT_PID_TYPE, DATASET_PID_TYPE
from publications.datasets.record import DatasetDraftRecord, DatasetRecord


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

            return {
                'url': published[0].published_context.record.canonical_url,
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


def handle_revert_approval(sender, force=False, **kwargs):
    if isinstance(sender, DatasetRecord):
        print('reverting dataset approval', sender)
        # TODO: send mail notification to interested people
        record_pid = PersistentIdentifier.query. \
            filter_by(pid_type=DATASET_PID_TYPE, object_uuid=sender.id).one()
        try:
            unpublished: List[PublishedDraftRecordPair] = \
                current_drafts.unpublish(sender, record_pid)
            db.session.commit()
            return {
                'url': unpublished[0].draft_context.record.canonical_url,
                'pid_type': unpublished[0].draft_context.record_pid.pid_type,
                'pid': unpublished[0].draft_context.record_pid.pid_value,
            }
        except:
            traceback.print_exc()
            raise


def handle_publish(sender, **kwargs):
    if isinstance(sender, DatasetRecord):
        print('making dataset public', sender)
        # TODO: send mail notification to interested people


def handle_unpublish(sender, **kwargs):
    if isinstance(sender, DatasetRecord):
        print('making dataset private', sender)
        # TODO: send mail notification to interested people


def handle_delete_draft(sender, **kwargs):
    if isinstance(sender, DatasetDraftRecord):
        print('deleting draft dataset', sender)
        sender.delete()
        record_pid = PersistentIdentifier.query. \
            filter_by(pid_type=DATASET_DRAFT_PID_TYPE, object_uuid=sender.id).one()
        record_pid.delete()
        db.session.commit()

        indexer = current_drafts.indexer_for_record(sender)
        indexer.delete(sender, refresh=True)

        return {
            'status': 'ok'
        }
