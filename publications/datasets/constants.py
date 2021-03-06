# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

DATASET_ALLOWED_SCHEMAS = ('datasets/publication-dataset-v1.0.0.json',)
DATASET_PREFERRED_SCHEMA = 'datasets/publication-dataset-v1.0.0.json'

DATASET_PID_TYPE = 'datset'
DATASET_DRAFT_PID_TYPE = 'dpsdat'
DATASET_ALL_PID_TYPE = 'apsdat'

DATASET_RECORD_CLASS = 'publications.datasets.record.DatasetRecord'
DATASET_DRAFT_RECORD_CLASS = 'publications.datasets.record.DatasetDraftRecord'
DATASET_ALL_RECORD_CLASS = 'publications.datasets.record.AllDatasetsRecord'
