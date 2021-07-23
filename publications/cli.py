# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Publications API cli commands."""
import json
import os
import subprocess
import tempfile
import traceback
from os.path import basename

import click
import tqdm
from flask import current_app
from flask.cli import with_appcontext
from invenio_app.factory import create_api
from invenio_db import db
from invenio_files_rest.models import ObjectVersion, FileInstance, Bucket
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import _records_state
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from json_schema_for_humans.generate import generate_from_file_object
from jsonref import JsonRef
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
        'oarepo',
        'index',
        'destroy',
        '--yes-i-know',
        '--force'
    ])

    subprocess.call([
        'oarepo',
        'index',
        'init',
        '--force'
    ])

    db.session.commit()


@publications.command('schema-docs')
@click.argument('schemas', nargs=-1)
@with_appcontext
def schema_docs(schemas):
    """Generates jsonschema docs for data models."""
    for schema_path in schemas:
        click.secho(f'Generating docs for schema {schema_path}')
        schema = current_jsonschemas.get_schema(schema_path, with_refs=False, resolved=False)
        schema = JsonRef.replace_refs(
            schema,
            jsonschema=True,
            base_uri=current_app.config.get('JSONSCHEMAS_HOST'),
            loader=_records_state.loader_cls(),
        )

        # TODO: this is necessary to resolve JSONRefs in allOf
        schema = json.loads(json.dumps(schema, default=lambda x: x.__subject__))

        # Generate and save html docs for the schema
        with tempfile.NamedTemporaryFile(mode="w+") as schema_source:
            schema_source.write(json.dumps(schema))
            schema_source.flush()

            with open(f'docs/schemas/{basename(schema_path.rstrip(".json"))}.html', mode='w+') as result_file:
                click.secho(f'Writing schema docs to {result_file.name}', color='green')
                generate_from_file_object(
                    schema_file=schema_source,
                    result_file=result_file,
                    minify=True,
                    expand_buttons=True
                )

    # Generate and save schema index page
    index_md = r"""---
layout: default
---

# Data Models Schema Docs

"""
    for f in os.listdir('docs/schemas/'):
        if f.endswith('.html'):
            index_md += f'- [{f.rstrip(".html")}](./{f})\n'

    with open(f'docs/schemas/index.md', mode='w+') as index_file:
        index_file.write(index_md)


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
