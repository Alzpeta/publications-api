import json
import multiprocessing as mp
import os
import sys
from pprint import pprint
from urllib.parse import urlencode, urlparse

import bleach
import dateutil
import requests
from boltons.iterutils import remap
from s3_client_lib.s3_multipart_client import upload_part

from publications.datasets.marshmallow import PublicationDatasetMetadataSchemaV1

TOKEN = sys.argv[1]
DATA_URL = sys.argv[2] if len(sys.argv) > 2 else 'https://localhost:8080/'
DRY_RUN = False
COMPUTED_FIELDS = ['stats', 'links', 'revision', 'conceptrecid', 'conceptdoi', 'id', 'owners']
UNSUPPORTED_FIELDS = ['access_right', 'access_right_category',
                      'relations', 'meeting', 'method', 'language', 'doi', 'license', 'communities', 'created']


def validate_dataset(dataset_json):
    schema = PublicationDatasetMetadataSchemaV1(
        context=dict(
            max_words=100000,
            max_length=100000
        ))
    try:
        return schema.load(dataset_json)
    except:
        pprint(dataset_json)
        raise


def sanitize_strings(data):
    def sanitize(p, k, v):
        if isinstance(v, str):
            return (k, bleach.clean(v, [
                'div', 'p', 'span', 'b', 'ul', 'li', 'ol', 'sub', 'sup', 'pre',
                'a', 'blockquote',
                'h1', 'h2', 'h3', 'h4', 'h5',
                'strong', 'em',
                'br',
            ], strip=True, strip_comments=True))
        return k, v

    return remap(data, sanitize)


def taxonomy_reference(code, term):
    return dict(
        links=dict(
            self=f'{DATA_URL}2.0/taxonomies/{code}/{term}'
        )
    )


def publish_dataset(dataset_json, id):
    col_url = DATA_URL + 'cesnet/datasets/draft/?access_token=%s' % TOKEN
    dataset_url = DATA_URL + 'cesnet/datasets/draft/%s?access_token=%s' % (id, TOKEN)

    headers = {'Content-type': 'application/json'}

    dataset_json.pop('_files', None)

    resp = requests.get(dataset_url, verify=False)
    if resp.status_code == 200:
        resp = requests.put(
            dataset_url, data=json.dumps(dataset_json), headers=headers, verify=False
        )
    else:
        resp = requests.post(
            col_url, data=json.dumps(dataset_json), headers=headers, verify=False
        )
    if resp.status_code not in (200, 201):
        print(resp.status_code)
        print(resp.content)
        raise Exception()
    dataset_url = resp.json().get('links', {}).get('self', None)
    return dataset_url


def upload_file(files_url, files_dir, fle, published_files):
    base_key = key = fle['key']
    idx = 0
    while key in published_files:
        key = f'{idx}-{base_key}'
        idx += 1
    published_files.add(key)

    fle.pop("bucket", None)
    fle.pop("checksum", None)
    fle.pop("file_id", None)
    fle.pop("iiif", None)
    orig_size = fle.pop("size", None)
    fle.pop("version_id", None)

    files_url += ('&' if urlparse(files_url).query else '?') + urlencode({
        'multipart': True
    })

    resp = requests.post(
        files_url,
        json={
            'key': key,
            'size': orig_size,
            'multipart_content_type': fle.get('type')
        },
        verify=False
    )
    if resp.status_code not in (200, 201):
        print(resp.status_code)
        print(resp.content)
        raise Exception()
    mp_conf = resp.json()['multipart_upload']
    chunk_size = mp_conf['chunk_size']

    parts = []
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

    filename = os.path.join(files_dir, f'{key}.data')
    pool = mp.Pool(mp.cpu_count())
    futures = []

    if not os.path.exists(filename):
        with open(filename, 'wb') as fout:
            fout.write(os.urandom(orig_size))
            fout.flush()

    for i in range(0, mp_conf['num_chunks']):
        url = mp_conf['parts_url'][i]
        part_no = i + 1
        cursor = i * chunk_size
        futures.append(pool.apply_async(upload_part, args=[url, filename, cursor, part_no, chunk_size]))
    pool.close()
    pool.join()
    for fut in futures:
        part = fut.get()
        if part is not None:
            parts.append(part)

    resp = requests.post(
        mp_conf['complete_url'],
        json={
            'parts': parts
        },
        verify=False
    )
    if resp.status_code not in (200, 201):
        print(resp.status_code)
        print(resp.content)
        raise Exception()


def generate_access(metadata):
    """Generates access metadata section.

        https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_access
    """
    return {
        'record': 'restricted',
        'files': 'restricted',
        'owned_by': []
    }


def generate_creators(metadata):
    """Generates record creators metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_creators
    """
    creators = []
    for creator in metadata['creators']:
        c = {
            'person_or_org': {
                'type': 'personal',
                'family_name': creator['name'].split(',')[0],
                'given_name': creator['name'].split(',')[-1].strip()
            }
        }
        orcid = creator.pop('orcid', None)
        if orcid:
            c['person_or_org']['identifiers'] = [{'identifier': orcid, 'scheme': 'orcid'}]

        aff = creator.pop('affiliation', None)
        if aff:
            c['affiliations'] = [{'name': aff}]

        creators.append(c)

    return creators


def generate_languages(metadata):
    """Generates languages metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_languages
    """
    lang = metadata.pop('language', None)
    languages = []
    if not lang:
        lang = 'eng'

    languages.append(taxonomy_reference('languages', lang))

    return languages


def generate_resource_type(metadata):
    """Generates resource type taxonomy field metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_resource_type
    """
    # types: Taxonomy = current_flask_taxonomies.get_taxonomy('resourceType')
    rtype = metadata['resource_type'].pop('type')
    if rtype == 'dataset':
        rtype = 'datasets'

    return {
        'type': taxonomy_reference('resourceType', rtype)
    }


def generate_record_identifiers(metadata):
    """Generates additional record identifiers metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_identifiers
    """
    return [{'identifier': metadata.pop('doi'), 'scheme': 'doi'}]


def generate_related_identifiers(metadata):
    """Generates related identifiers field metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_related_identifiers
    """
    identifiers = []
    for identifier in metadata.pop('related_identifiers', []):
        identifiers.append({
            'relation_type': taxonomy_reference('itemRelationType', str(identifier['relation']).lower()),
            'identifier': identifier['identifier'],
            'scheme': identifier['scheme'].lower()
        })

    return identifiers


def generate_rights(metadata):
    """Generates metadata for license rights field.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_rights
    """
    rights = []

    # Maps license id codes to licenses taxonomy term paths
    licmap = {
        'CC-BY-4.0': 'cc/4-0/4-by',
        'CC0-1.0': 'cc/zero/1-0'
    }

    license = metadata.pop('license')
    if license:
        rights.append(taxonomy_reference('licenses', licmap[license['id']]))

    return rights


def generate_secondary_communities(metadata):
    """Generates record's secondary communities metadata."""
    return [com['id'] for com in metadata.pop('communities', [])]


def generate_dates(metadata):
    """Generate date list from metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_rights
    """
    created = metadata.pop('created', None)
    dates = []
    create_date = dateutil.parser.parse(created)

    if created:
        dates.append({
            'date': create_date.strftime('%Y-%m-%d'),
            'type': 'created'
        })

    return dates


def convert_to_rdm(metadata):
    """Convert a current Zenodo dataset metadata to new RDM format.

        https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#tab-pane_allOf_i0_allOf_i1
    """
    metadata['created'] = dataset_json.pop('created')
    metadata['access'] = generate_access(metadata)
    metadata['creator'] = 'dataset-ingest@cesnet.cz'
    metadata['creators'] = generate_creators(metadata)
    metadata['languages'] = generate_languages(metadata)
    metadata['resource_type'] = generate_resource_type(metadata)
    metadata['identifiers'] = generate_record_identifiers(metadata)
    metadata['related_identifiers'] = generate_related_identifiers(metadata)
    metadata['rights'] = generate_rights(metadata)
    metadata['_communities'] = generate_secondary_communities(metadata)
    metadata['dates'] = generate_dates(metadata)

    title = metadata.pop('title')
    metadata['title'] = {'en': title, '_': title}
    abstract = metadata.pop('description')
    metadata['abstract'] = {'en': abstract, '_': abstract}
    notes = metadata.pop('notes', None)
    if notes:
        metadata['additional_descriptions'] = [{'en': notes, '_': notes}]

    # Drop unsupported fields
    for fld in UNSUPPORTED_FIELDS:
        metadata.pop(fld, None)

    return metadata


def import_dataset(pid, dataset_json, files_dir):
    files = dataset_json.pop('files', [])
    id = dataset_json['id']

    # Drop computed internal fields which we don't need
    for fld in COMPUTED_FIELDS:
        dataset_json.pop(fld, None)

    metadata = dataset_json['metadata']
    metadata = sanitize_strings(metadata)
    metadata = convert_to_rdm(metadata)

    dataset_json = validate_dataset(metadata)
    published_files = set()
    print('dataset json', dataset_json)
    dataset_url = publish_dataset(dataset_json, id)
    print('Created Dataset DRAFT on: ', dataset_url)
    files_url = dataset_url + '/files/?access_token=%s' % TOKEN

    for fle in files:
        upload_file(files_url, files_dir, fle, published_files)


if __name__ == '__main__':
    from oarepo_micro_api.wsgi import application

    with application.app_context():
        for d in os.listdir('data'):
            dd = os.path.join('data', d)
            if not os.path.isfile(dd):
                continue
            if not d.endswith('.json'):
                continue
            pid = d[:-5]
            with open(dd) as f:
                dataset_json = json.loads(f.read())
            try:
                files_dir = os.path.join('data', '%s_files' % pid)
                import_dataset(pid, dataset_json, files_dir)
            except:
                print('Error at code', pid)
                raise
