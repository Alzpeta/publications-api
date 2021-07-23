#!/bin/bash

export FLASK_ENV=development

oarepo run --cert development/server.crt --key development/server.key --port 8080 --host 127.0.0.1
