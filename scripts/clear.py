#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OA Repository Demo is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import subprocess

from invenio_app.factory import create_app
from invenio_db import db
from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets
from oarepo_references.models import RecordReference, ClassName, ReferencingRecord
from sqlalchemy_continuum import version_class, versioning_manager


def clear():
    app = create_app()
    with app.app_context():
        # pprint(app.config)

        # remove database stuff
        RecordsBuckets.query.delete()
        RecordMetadata.query.delete()
        PersistentIdentifier.query.delete()
        ObjectVersion.query.delete()
        FileInstance.query.delete()
        Bucket.query.delete()
        version_cls = version_class(RecordMetadata)
        version_cls.query.delete()
        versioning_manager.transaction_cls.query.delete()
        RecordReference.query.delete()
        ReferencingRecord.query.delete()
        ClassName.query.delete()

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


if __name__ == '__main__':
    clear()
