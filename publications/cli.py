# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Publications API cli commands."""
import json

import click
import requests
from flask import url_for, current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search
from oarepo_rdm_records.cli import create_fake_record
from publications.datasets.record import DatasetDraftRecord


@click.group()
def dataset_records():
    """Do Data set records commands."""
    pass


def create_dataset_record(record_json, token):
    headers = {'Content-type': 'application/json'}
    dat_url = f'https://127.0.0.1:5000/api/draft/publications/datasets/?access_token={token}'
    record_json.pop('_files', None)

    print(dat_url)
    resp = requests.post(
        dat_url, data=json.dumps(record_json), headers=headers, verify=False
    )
    if resp.status_code not in (200, 201):
        print(resp.status_code)
        print(resp.content)
        raise Exception()

    return resp.content


@dataset_records.command('demo')
@click.argument('token')
@with_appcontext
def demo(token):
    """Create 10 fake data set records for demo purposes."""
    click.secho('Creating demo records...', fg='blue')

    for _ in range(10):
        data = create_fake_record()
        res = create_dataset_record(data, token)
        click.secho(str(res), fg='red')

    click.secho('Created records!', fg='green')
