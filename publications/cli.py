# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Publications API cli commands."""
import json
import traceback

import click
import tqdm
from flask.cli import with_appcontext
from invenio_app.factory import create_api
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from publications.articles.constants import ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE
from publications.articles.record import ArticleRecord, ArticleDraftRecord
from publications.datasets.constants import DATASET_PID_TYPE, DATASET_DRAFT_PID_TYPE
from publications.datasets.record import DatasetRecord, DatasetDraftRecord


@click.group()
def dataset_records():
    """Do Data set records commands."""
    pass


@dataset_records.command('reindex')
@click.option(
    '--raise-on-error/--skip-errors', default=True,
    help='Controls if Elasticsearch bulk indexing errors raise an exception.')
@click.option(
    '--only',
    help='Index only this item')
@with_appcontext
@click.pass_context
def dataset_reindex(ctx, raise_on_error=True, only=None):
    version_type = None  # elasticsearch version to use
    api = create_api()
    with api.app_context():
        def reindex_pid(pid_type, RecordClass):
            index_name = None
            indexer = RecordIndexer()
            for pid in tqdm.tqdm(PersistentIdentifier.query.filter_by(
                    pid_type=pid_type, object_type='rec', status=PIDStatus.REGISTERED.value)):
                record = RecordClass.get_record(pid.object_uuid)
                if only and str(record.id) != only:
                    continue
                try:
                    index_name, doc_type = indexer.record_to_index(record)
                    index_name = build_alias_name(index_name)
                    # print('Indexing', record.get('id'), 'into', index_name)
                    indexer.index(record)
                except:
                    with open('/tmp/indexing-error.json', 'a') as f:
                        print(json.dumps(record.dumps(), indent=4, ensure_ascii=False), file=f)
                        traceback.print_exc(file=f)
                    if raise_on_error:
                        raise
            if index_name:
                current_search_client.indices.refresh(index_name)
                current_search_client.indices.flush(index_name)

        # reindex all objects
        reindex_pid(DATASET_PID_TYPE, DatasetRecord)
        reindex_pid(DATASET_DRAFT_PID_TYPE, DatasetDraftRecord)


@click.group()
def article_records():
    """Do Data set records commands."""
    pass


@article_records.command('reindex')
@click.option(
    '--raise-on-error/--skip-errors', default=True,
    help='Controls if Elasticsearch bulk indexing errors raise an exception.')
@click.option(
    '--only',
    help='Index only this item')
@with_appcontext
@click.pass_context
def article_reindex(ctx, raise_on_error=True, only=None):
    version_type = None  # elasticsearch version to use
    api = create_api()
    with api.app_context():
        def reindex_pid(pid_type, RecordClass):
            index_name = None
            indexer = RecordIndexer()
            for pid in tqdm.tqdm(PersistentIdentifier.query.filter_by(
                    pid_type=pid_type, object_type='rec', status=PIDStatus.REGISTERED.value)):
                record = RecordClass.get_record(pid.object_uuid)
                if only and str(record.id) != only:
                    continue
                try:
                    index_name, doc_type = indexer.record_to_index(record)
                    index_name = build_alias_name(index_name)
                    # print('Indexing', record.get('id'), 'into', index_name)
                    indexer.index(record)
                except:
                    with open('/tmp/indexing-error.json', 'a') as f:
                        print(json.dumps(record.dumps(), indent=4, ensure_ascii=False), file=f)
                        traceback.print_exc(file=f)
                    if raise_on_error:
                        raise
            if index_name:
                current_search_client.indices.refresh(index_name)
                current_search_client.indices.flush(index_name)

        # reindex all objects
        reindex_pid(ARTICLE_PID_TYPE, ArticleRecord)
        reindex_pid(ARTICLE_DRAFT_PID_TYPE, ArticleDraftRecord)
