#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OA Repository Demo is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

set -e

INSTANCE_PATH=${INVENIO_INSTANCE_PATH:=.venv/var/instance}

# Clean redis
echo 'Initializing DB, ES, Cache and MQ'
oarepo shell --no-term-title -c "import redis; redis.StrictRedis.from_url(app.config['CACHE_REDIS_URL']).flushall(); print('Cache cleared')"
oarepo db create
oarepo index destroy --force --yes-i-know
oarepo index init
oarepo index queue init purge

echo 'Importing Taxonomic trees'
oarepo taxonomies init
oarepo taxonomies import "${INSTANCE_PATH}/taxonomies/contributorType.xlsx"
oarepo taxonomies import "${INSTANCE_PATH}/taxonomies/languages.xlsx"
oarepo taxonomies import "${INSTANCE_PATH}/taxonomies/licenses.xlsx"
oarepo taxonomies import "${INSTANCE_PATH}/taxonomies/relationType.xlsx"
oarepo taxonomies import "${INSTANCE_PATH}/taxonomies/resourceType.xlsx"

echo 'Initializing default S3 storage bucket location'
oarepo files location --default 'default-s3' s3://oarepo

# Create roles to manage access
echo 'Creating system roles to manage access'
oarepo roles create ingester -d 'data ingester'
oarepo roles create curator -d 'curator'
oarepo roles create admin -d 'system administrator'

# Create system users
echo 'Creating dataset-ingest user'
read -s -p "Password:" datinpass
oarepo users create dataset-ingest@cesnet.cz --password $datinpass
oarepo users activate dataset-ingest@cesnet.cz

echo 'Assigning users to roles'
oarepo roles add dataset-ingest@cesnet.cz ingester
oarepo access allow files-rest-bucket-read role ingester
oarepo access allow files-rest-bucket-update role ingester

echo 'Creating demo-ingest token (use for `./example/load_data.py ${TOKEN}`)'
oarepo tokens create -n demo-ingest -u dataset-ingest@cesnet.cz

oarepo access allow superuser-access role admin

echo 'Setting up default CESNET community'
oarepo oarepo:communities create cesnet 'CESNET community' --description 'Default CESNET OA repository community'
oarepo oarepo:communities actions list -c cesnet

echo 'Thats all folks!'
echo
echo "To import some example datasets, run: python example/load_data.py ${demo-ingest-token} https://${oarepo_SERVER_NAME}/"
