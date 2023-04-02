from abc import ABCMeta, abstractmethod
from typing import List

import numpy as np
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
            title_embed=np.array(title_embed).tolist(),
            summary_embed=np.array(summary_embed).tolist(),
            content_embed=np.array(content_embed).tolist()
        )
        return article_with_embeddings
