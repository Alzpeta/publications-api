#!/bin/bash

cd `dirname $0`

export FLASK_ENV=development 

invenio run --cert development/server.crt --key development/server.key
