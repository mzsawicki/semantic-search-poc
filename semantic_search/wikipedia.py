import functools

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
