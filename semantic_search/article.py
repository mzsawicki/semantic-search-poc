from dataclasses import dataclass
from typing import List


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
    title_embed: List[float]
    summary_embed: List[float]
    content_embed: List[float]
