# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

# ARTICLE_ALLOWED_SCHEMAS = ('https://localhost:5000/schemas/publications/publication-article-v1.0.0.json',)
# ARTICLE_PREFERRED_SCHEMA = 'https://localhost:5000/schemas/publications/publication-article-v1.0.0.json'
ARTICLE_ALLOWED_SCHEMAS = ('articles/publication-article-v1.0.0.json',)
ARTICLE_PREFERRED_SCHEMA = 'articles/publication-article-v1.0.0.json'

ARTICLE_PID_TYPE = 'pubart'
ARTICLE_DRAFT_PID_TYPE = 'dpsart'
ARTICLE_ALL_PID_TYPE = 'apsart'

ARTICLE_RECORD_CLASS = 'publications.articles.record.ArticleRecord'
ARTICLE_DRAFT_RECORD_CLASS = 'publications.articles.record.ArticleDraftRecord'
ARTICLE_ALL_RECORD_CLASS = 'publications.articles.record.AllArticlesRecord'
