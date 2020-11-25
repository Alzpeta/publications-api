#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OA Repository Demo is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

set -e

# Clean redis
invenio shell --no-term-title -c "import redis; redis.StrictRedis.from_url(app.config['CACHE_REDIS_URL']).flushall(); print('Cache cleared')"
invenio db create
invenio index destroy --force --yes-i-know
invenio index init
invenio index queue init purge
invenio files location --default 'default-s3' s3://oarepo

# Create roles to manage access
invenio roles create ingester -d 'data ingester'
invenio roles create curator -d 'curator'
invenio roles create admin -d 'system administrator'

# Create system users
echo 'Creating dataset-ingest user'
read -s -p "Password:" datinpass
invenio users create dataset-ingest@cesnet.cz --password $datinpass
invenio users activate dataset-ingest@cesnet.cz

invenio roles add dataset-ingest@cesnet.cz ingester

echo 'Creating demo-ingest token (use for `invenio dataset-records demo ${TOKEN}`)'
invenio tokens create -n demo-ingest -u dataset-ingest@cesnet.cz

invenio access allow superuser-access role admin

echo 'Thats all folks!'