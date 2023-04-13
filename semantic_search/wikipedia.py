import functools
from pathlib import Path
from typing import List

import wikipedia

from semantic_search.article import Article


@functools.lru_cache()
def fetch_article(title: str) -> Article:
    page = wikipedia.page(title)
    article = Article(
        title=page.title,
        summary=page.summary,
        content=page.content
    )
    return article


def scrap_from_titles_file(path: Path) -> List[Article]:
    with open(path, 'r') as f:
        titles = f.readlines()
    articles = [fetch_article(title) for title in titles]
    return articles
