# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_indexer.api import RecordIndexer


class CommitingRecordIndexer(RecordIndexer):
    def index(self, record, arguments=None, **kwargs):
        ret = super().index(record, arguments=arguments, **kwargs)
        index, doc_type = self.record_to_index(record)
        self.client.indices.flush(index=index)
        return ret
