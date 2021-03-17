# publications-api

[![image][]][1]
[![image][2]][3]
[![image][4]][5]
[![image][6]][7]

OpenAccess repository application REST API for publishing scientific dataset
records and corresponding journal articles linked with the datasets. Metadata
model used for datasets  and articles is based
on [OARepo-RDM-Records](https://github.com/oarepo/oarepo-rdm-records)
and [OARepo-documents](https://github.com/oarepo/oarepo-documents).

## Features

* S3 storage support for dataset files
* OpenID Connect authentication
* Record FSM state management for approvement processes
* Record references tracking
* Harvesting of article metadata from DOI

## Instalation

To setup your development environment, follow these steps:

0) Create project virtualenv
   ```shell
   python3.9 -m venv .venv
   ```
1) Install necessary project dependencies
    ```shell
    poetry install
    ```

2) Create an S3 account and bucket on your S3 storage provider of choice.
   This storage will be used for managing dataset data.
3) Put the S3 access configuration into your Invenio server config (e.g. `invenio.cfg`):
    ```python
    INVENIO_S3_TENANT=None
    INVENIO_S3_ENDPOINT_URL='https://s3.example.org'
    INVENIO_S3_ACCESS_KEY_ID='your_access_key'
    INVENIO_S3_SECRET_ACCESS_KEY='your_secret_key'
    ```
4) Start up project infrastructure in Docker
   ```shell
   docker-compose up -d
   ```
5) Configure your Invenio server runtime environment (see 
   [.env.sample](https://github.com/oarepo/publications-api/blob/master/.env.sample)) or `invenio.cfg`

6) Create the ltree extension ``create extension ltree;`` in the project database
7) Run project setup script. Doing so will initialize all tables, indices and user roles. It will also create
   an ingester user and corresponding API TOKEN which you may need later on.
   ```shell
   bash setup.sh
   ```
8) Start the Publications API server, e.g. by running:
   ```shell
   ./scripts/run.sh
   ```
9) Install and run its [UI counterpart](https://github.com/oarepo/publications-ui).
10) (_OPTIONAL_) Import sample dataset collection
   (see [README](https://github.com/oarepo/publications-api/example/data/README.md)). You will need an
   API token of a user with the ingester role (created in the previous step).
   ```shell
   cd example/
   export INGEST_TOKEN=<put your token here>
   export UI_ADDRESS='https://127.0.0.1:5000'
   poetry run python load_data.py $INGEST_TOKEN ${UI_ADDRESS}/
   ```
## Usage

You can check if everything worked out by listing the API of dataset collection:

```shell
curl -k  https://127.0.0.1:5000/datasets/ | jq
```


  [image]: https://img.shields.io/github/license/oarepo/publications-api.svg
  [1]: https://github.com/oarepo/publications-api/blob/master/LICENSE
  [2]: https://img.shields.io/travis/oarepo/publications-api.svg
  [3]: https://travis-ci.com/oarepo/publications-api
  [4]: https://img.shields.io/coveralls/oarepo/publications-api.svg
  [5]: https://coveralls.io/r/oarepo/publications-api
  [6]: https://img.shields.io/pypi/v/publications-api.svg
  [7]: https://pypi.org/pypi/publications-api