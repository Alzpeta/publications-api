from flask import current_app, session, request_started
from invenio_base.signals import app_loaded
from invenio_search import current_search
from wrapt import ObjectProxy


class IndicesProxy(ObjectProxy):
    def create(self, index=None, body=None, **kwargs):
        if 'aliases' in body:
            prefix = current_app.config.get('SEARCH_INDEX_PREFIX', '')
            body['aliases'] = {
                k.replace('{PREFIX}', prefix): v for k, v in body['aliases'].items()
            }
        return self.__wrapped__.create(index=index, body=body, **kwargs)


class ElasticsearchProxy(ObjectProxy):
    def __init__(self, wrapped):
        super().__init__(wrapped)
        self.__wrapped_indices__ = None

    @property
    def indices(self):
        if not self.__wrapped_indices__:
            self.__wrapped_indices__ = IndicesProxy(self.__wrapped__.indices)
        return self.__wrapped_indices__


# @request_started.connect
# def force_default_language(sender, *args, **kwargs):
#     session[current_app.config['I18N_SESSION_KEY']] = current_app.config['BABEL_DEFAULT_LOCALE']


@app_loaded.connect
def patch_invenio(sender, *args, app=None, **kwargs):
    with app.app_context():
        client = current_search.client
        if not isinstance(client, ElasticsearchProxy):
            current_search._client = ElasticsearchProxy(client)