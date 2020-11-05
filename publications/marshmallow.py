# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import flask
from oarepo_multilingual.marshmallow import MultilingualStringV2
from oarepo_taxonomies.marshmallow import TaxonomyField


class TitledMixin:
    title = MultilingualStringV2()


def TitledTaxonomyField(*args, **kwargs):
    return TaxonomyField(
        *args, name=kwargs.pop('name', 'TitledTaxonomyField'),
        mixins=[
            TitledMixin,
            *(kwargs.pop('mixins', []))
        ],
        **kwargs
    )


def check_multilingual_string_length(val, max_words=100, max_length=5000):
    for lang, text in val.items():
        plain = flask.Markup(text).striptags()
        word_count = len(plain.split())
        if word_count > max_words or len(text) > max_length:
            return False
    return True
