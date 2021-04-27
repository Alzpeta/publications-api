# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# CESNET OA Repository Demo is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
# Dockerfile that builds a fully functional image of your app.
ARG DEPENDENCIES_VERSION=latest
FROM inveniosoftware/centos8-python:3.8

COPY ./ .
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

# Install 3rdparty unpublished deps
RUN pip install poetry
RUN poetry config virtualenvs.create false
WORKDIR 3rdparty/s3-client
RUN poetry install
WORKDIR ../..
RUN pip install 3rdparty/s3-client
USER uwsgi
RUN poetry install
ENTRYPOINT [ "bash", "-c"]
