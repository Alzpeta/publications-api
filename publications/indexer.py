# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_indexer.api import RecordIndexer
from invenio_search.utils import build_alias_name
from oarepo_records_draft.record import record_to_index as draft_record_to_index


def record_to_index(record):
    index = getattr(record, 'index_name', None)
    if index:
        return index, '_doc'

    return draft_record_to_index(record)


class CommitingRecordIndexer(RecordIndexer):
    def index(self, record, arguments=None, **kwargs):
        ret = super().index(record, arguments=arguments, **kwargs)
        index, doc_type = self.record_to_index(record)
        index = build_alias_name(index)
        self.client.indices.refresh(index=index)
        return ret
