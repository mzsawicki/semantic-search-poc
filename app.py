from aiohttp import web

from semantic_search.config import Config
from semantic_search.elastic import elasticsearch_local, elastic_cloud
from semantic_search.http import reindex, search
from semantic_search.model import TensorFlowHubModel, Embedder


async def setup_elasticsearch(application):
    config = Config()
    elasticsearch_integration_type = config['elasticsearch_integration_type']
    if elasticsearch_integration_type == 'LOCAL':
        elasticsearch_config = config['elasticsearch_local']
        hosts = elasticsearch_config['hosts']
        user = elasticsearch_config['user']
        password = elasticsearch_config['password']
        elasticsearch_ = elasticsearch_local(hosts, user, password)
    elif elasticsearch_integration_type == 'CLOUD':
        elasticsearch_config = config['elastic_cloud']
        cloud_id = elasticsearch_config['cloud_id']
        user = elasticsearch_config['user']
        password = elasticsearch_config['password']
        elasticsearch_ = elastic_cloud(cloud_id, user, password)
    else:
        raise RuntimeError('Invalid elasticsearch_integration_type')

    application['elastic'] = elasticsearch_
    yield
    await elasticsearch_.close()


async def setup_text_embedder(application):
    config = Config()
    embedder = Embedder(TensorFlowHubModel(config['tensorflow_hub']['model_url']))
    application['embedder'] = embedder
    yield


def run():
    config = Config()
    port = config['api']['port']
    application = web.Application()
    application.add_routes([
        web.post('/search', search),
        web.post('/reindex', reindex)
    ])
    application.cleanup_ctx.append(setup_elasticsearch)
    application.cleanup_ctx.append(setup_text_embedder)
    web.run_app(application, port=port)


if __name__ == '__main__':
    run()
