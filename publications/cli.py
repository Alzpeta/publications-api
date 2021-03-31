# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Publications API cli commands."""
import json
import subprocess
import traceback

import click
import tqdm
from flask.cli import with_appcontext
from invenio_app.factory import create_api
from invenio_db import db
from invenio_files_rest.models import ObjectVersion, FileInstance, Bucket
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from sqlalchemy_continuum import version_class, versioning_manager

from publications.articles.constants import ARTICLE_PID_TYPE, ARTICLE_DRAFT_PID_TYPE
from publications.articles.record import ArticleRecord, ArticleDraftRecord
from publications.datasets.constants import DATASET_PID_TYPE, DATASET_DRAFT_PID_TYPE
from publications.datasets.record import DatasetRecord, DatasetDraftRecord


@click.group()
def publications():
    """Commands for publications repository."""
    pass


@publications.command('clear')
@with_appcontext
@click.pass_context
def clear(ctx, raise_on_error=True, only=None):
    """Clear all record data in publications repository."""
    RecordsBuckets.query.delete()
    RecordMetadata.query.delete()
    PersistentIdentifier.query.delete()
    ObjectVersion.query.delete()
    FileInstance.query.delete()
    Bucket.query.delete()
    version_cls = version_class(RecordMetadata)
    version_cls.query.delete()
    versioning_manager.transaction_cls.query.delete()
    # RecordReference.query.delete()
    # ReferencingRecord.query.delete()
    # ClassName.query.delete()

    subprocess.call([
        'invenio',
        'index',
        'destroy',
        '--yes-i-know',
        '--force'
    ])

    subprocess.call([
        'invenio',
        'index',
        'init',
        '--force'
    ])

    db.session.commit()


@publications.group('datasets')
def datasets():
    """Commands for dataset collection management."""


@publications.group('articles')
def articles():
    """Commands for article collection management."""


@datasets.command('reindex')
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


@articles.command('reindex')
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
