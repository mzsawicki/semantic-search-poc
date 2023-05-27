from aiohttp import web

from semantic_search.config import Config
from semantic_search.elastic import ElasticSearchGateway, IndexNotAvailable
from semantic_search.mappings import UNIVERSAL_SENTENCE_ENCODER_MAPPING
from semantic_search.model import Embedder
from semantic_search.wikipedia import scrap_from_titles_file


async def search(request):
    elastic: ElasticSearchGateway = request.app['elastic']
    embedder: Embedder = request.app['embedder']

    request_data = request.json()
    search_query = request_data['query']
    search_query_embedding = await embedder.embed_phrase(search_query)

    try:
        results = await elastic.search(search_query, search_query_embedding)
    except IndexNotAvailable:
        return web.Response(status=503,
                            body="Elasticsearch index not available. Please POST /reindex")

    return web.json_response(data=results, status=200)


async def reindex(request):
    config = Config()

    elastic: ElasticSearchGateway = request.app['elastic']
    embedder: Embedder = request.app['embedder']

    titles_file = config['articles']['file']
    articles = scrap_from_titles_file(titles_file)

    if await elastic.index_available():
        await elastic.remove_index()
    await elastic.create_index(mappings=UNIVERSAL_SENTENCE_ENCODER_MAPPING)
    for article in articles:
        article_with_embeddings = await embedder.embed_article(article)
        await elastic.add_article(article_with_embeddings)

    return web.Response(status=200)


