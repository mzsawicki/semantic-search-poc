from semantic_search.config import config
from semantic_search.elastic import elasticsearch_local
from semantic_search.mappings import UNIVERSAL_SENTENCE_ENCODER_MAPPING
from semantic_search.model import TensorFlowHubModel, Embedder
from semantic_search.wikipedia import fetch_article


async def test_indexed_article_can_be_found_by_id():
    embedder = Embedder(TensorFlowHubModel(config['tensorflow_hub']['model_url']))
    hosts = config['elasticsearch_local']['hosts']
    user = config['elasticsearch_local']['user']
    password = config['elasticsearch_local']['password']
    async with elasticsearch_local(hosts, user, password, index_name='articles-test') as elasticsearch_:
        if not await elasticsearch_.index_available():
            await elasticsearch_.create_index(UNIVERSAL_SENTENCE_ENCODER_MAPPING)

        original_title = "Semantic search"
        article = fetch_article(original_title)
        article_with_embeddings = embedder.embed_article(article)

        indexed_article_id = await elasticsearch_.add_article(article_with_embeddings)
        found_article = await elasticsearch_.find_article_by_id(indexed_article_id)

        await elasticsearch_.remove_index()

    assert found_article.title == original_title