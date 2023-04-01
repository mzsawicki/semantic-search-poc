from semantic_search.config import config
from semantic_search.model import TensorFlowHubModel
from semantic_search.wikipedia import fetch_article


def test_model_returns_text_embeddings():
    model = TensorFlowHubModel(config['tensorflow_hub']['model_url'])
    article = fetch_article('Semantic search')
    embeds = model.embed([article.title, article.summary, article.content])
    assert len(embeds) == 3
