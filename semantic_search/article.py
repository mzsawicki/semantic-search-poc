from dataclasses import dataclass

import tensorflow as tf


@dataclass(frozen=True, init=True)
class Article:
    title: str
    summary: str
    content: str


@dataclass(frozen=True, init=True)
class ArticleWithEmbeddings:
    title: str
    summary: str
    content: str
    title_embed: tf.Tensor
    summary_embed: tf.Tensor
    content_embed: tf.Tensor
