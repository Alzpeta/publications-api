#!/bin/bash

export FLASK_ENV=development

invenio run --cert development/server.crt --key development/server.key --port 8080 --host 127.0.0.1
