# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Publication Repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

def titled_term(**kwargs):
    return {
        'type': 'taxonomy-term',
        'properties': {
            'title': {
                'type': 'multilingual'
            }
        }
    }