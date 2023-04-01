from abc import ABCMeta, abstractmethod
from typing import List

import tensorflow as tf
import tensorflow_hub as hub

from semantic_search.article import Article, ArticleWithEmbeddings


class TextEmbeddingModel(metaclass=ABCMeta):
    @abstractmethod
    def embed(self, text: List[str]) -> tf.Tensor:
        raise NotImplemented


class TensorFlowHubModel(TextEmbeddingModel):
    def __init__(self, hub_url: str):
        self._model = hub.load(hub_url)

    def embed(self, text: List[str]) -> tf.Tensor:
        embeddings = self._model(text)
        return embeddings


class Embedder:
    def __init__(self, model: TextEmbeddingModel):
        self._model = model

    def embed_article(self, article: Article) -> ArticleWithEmbeddings:
        title_embed, summary_embed, content_embed = self._model.embed([article.title, article.summary, article.content])
        article_with_embeddings = ArticleWithEmbeddings(
            title=article.title,
            summary=article.summary,
            content=article.content,
            title_embed=title_embed,
            summary_embed=summary_embed,
            content_embed=content_embed
        )
        return article_with_embeddings
