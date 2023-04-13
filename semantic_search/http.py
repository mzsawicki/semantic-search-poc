from dataclasses import asdict

from aiohttp import web

from semantic_search.config import Config
from semantic_search.elastic import ElasticSearchGateway, IndexNotAvailable
from semantic_search.model import Embedder
from semantic_search.wikipedia import scrap_from_titles_file


async def search(request):
    elastic: ElasticSearchGateway = request.app['elastic']
    search_query = request.query['query']

    try:
        results = await elastic.search(search_query)
    except IndexNotAvailable:
        return web.Response(status=503,
                            body="Elasticsearch index not available. Please POST /reindex")

    return web.json_response(data=results, status=200)


async def reindex(request):
    elastic: ElasticSearchGateway = request.app['elastic']
    embedder: Embedder = request.app['embedder']

    titles_file = Config.TITLES_FILE_PATH
    articles = scrap_from_titles_file(titles_file)

    if await elastic.index_available():
        await elastic.remove_index()
    await elastic.create_index()
    for article in articles:
        article_with_embeddings = await embedder.embed_article(article)
        await elastic.add_article(article_with_embeddings)

    return web.Response(status=200)


