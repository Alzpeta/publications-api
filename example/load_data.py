import json
import multiprocessing as mp
import os
import sys
from pprint import pprint
from urllib.parse import urlencode, urlparse

import bleach
import requests
from boltons.iterutils import remap
from s3_client_lib.s3_multipart_client import upload_part

from publications.datasets.marshmallow import PublicationDatasetMetadataSchemaV1

TOKEN = sys.argv[1]
DATA_URL = sys.argv[2] if len(sys.argv) > 2 else 'https://localhost:8080/'
DRY_RUN = False
UNSUPPORTED_FIELDS = ['access_right', 'access_right_category',
                      'relations', 'meeting', 'method']

    metadata['_communities'] = [com['id'] for com in metadata.pop('communities', [])]


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
        return (k, bleach.clean(v, [
            'div', 'p', 'span', 'b', 'ul', 'li', 'ol', 'sub', 'sup', 'pre',
            'a', 'blockquote',
            'h1', 'h2', 'h3', 'h4', 'h5',
            'strong', 'em',
            'br',
        ], strip=True, strip_comments=True))

    return remap(data, sanitize)


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

        https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_metadata_access
    """
    return {
        'record': True,
        'files': True,
        'owned_by': []
    }


def generate_creators(metadata):
    """Generates record creators metadata.

       https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#allOf_i0_allOf_i1_metadata_creators
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


def convert_to_rdm(metadata):
    """Convert a current Zenodo dataset metadata to new RDM format.

        https://oarepo.github.io/publications-api/schemas/publication-dataset-v1.0.0.html#tab-pane_allOf_i0_allOf_i1
    """
    
    metadata['created'] = dataset_json.pop('created')
    metadata['access'] = generate_access(metadata)
    metadata['creators'] = generate_creators(metadata)
    metadata['resource_type'].pop('title')
    metadata.pop('language', None)
    # TODO: update language mapping in oarepo-rdm-records to contain code prop!
    # if lang:
    #     metadata['language'] = {'code': lang[:2]}

    # Convert creators


    related = metadata.get('related_identifiers', None)
    if related:
        metadata['related_identifiers'] = [
            {
                'relation_type': str(r['relation']).lower(),
                'identifier': r['identifier'],
                'scheme': r['scheme'].lower()
            } for r in related]
    metadata['titles'] = [{'en': metadata.pop('title')}]
    metadata['identifiers'] = [{'identifier': metadata.pop('doi'), 'scheme': 'doi'}]
    metadata['abstract'] = {'description': {'en': metadata.pop('description')}, 'type': 'abstract'}
    notes = metadata.pop('notes', None)
    if notes:
        metadata['additional_descriptions'] = [{'description': {'en': notes}, 'type': 'other'}]
    license = metadata.pop('license')
    metadata['rights'] = [{'rights': license['id'], 'identifier': license['id']}]

    # Drop unsupported fields

    return metadata


def import_dataset(pid, dataset_json, files_dir):
    files = dataset_json.pop('files', [])
    id = dataset_json['id']
    metadata = dataset_json['metadata']
    metadata = sanitize_strings(metadata)
    metadata = convert_to_rdm(metadata)

    dataset_json = validate_dataset(metadata)
    published_files = set()

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
