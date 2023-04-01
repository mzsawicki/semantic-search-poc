from abc import ABCMeta, abstractmethod
from dataclasses import asdict
import re
from typing import List, Dict

from elasticsearch import AsyncElasticsearch

from semantic_search.article import ArticleWithEmbeddings


class ElasticsearchException(Exception):
    pass


class IndexNotAvailable(ElasticsearchException):
    pass


class ElasticSearchConfigurator(metaclass=ABCMeta):
    """
    Example uses Bonsai provided ElasticSearch which uses credentials-based auth
    To use different configuration, substitute your own concrete configurator class
    """
    @abstractmethod
    def configure_client(self) -> AsyncElasticsearch:
        raise NotImplemented


class BonsaiConfigurator(ElasticSearchConfigurator):
    def __init__(self, bonsai_url: str):
        self._url = bonsai_url

    def configure_client(self) -> AsyncElasticsearch:
        auth = re.search('https\:\/\/(.*)\@', self._url).group(1).split(':')
        host = self._url.replace('https://%s:%s@' % (auth[0], auth[1]), '')

        match = re.search('(:\d+)', host)
        if match:
            p = match.group(0)
            host = host.replace(p, '')
            port = int(p.split(':')[1])
        else:
            port = 443

        es_header = [{
            'host': host,
            'port': port,
            'use_ssl': True,
            'http_auth': (auth[0], auth[1])
        }]

        client = AsyncElasticsearch(es_header)
        return client


class ElasticSearchGateway:
    DEFAULT_INDEX_NAME = 'articles'

    def __init__(self, configurator: ElasticSearchConfigurator, index_name: str = DEFAULT_INDEX_NAME):
        self._client = configurator.configure_client()
        self._index_name = index_name

    async def index_available(self) -> bool:
        index_available = await self._client.indices.exists(index=self._index_name)
        return index_available

    async def create_index(self, mappings: Dict = None) -> None:
        await self._client.indices.create(index=self._index_name, body=mappings)

    async def remove_index(self) -> None:
        await self._client.indices.delete(index=self._index_name)

    async def add_article(self, article: ArticleWithEmbeddings) -> str:
        """Adds article to the index. Returns its id"""
        if not await self.index_available():
            raise IndexNotAvailable
        article_document = asdict(article)
        response = await self._client.index(index=self._index_name, body=article_document)
        return response["_id"]

    async def find_article_by_id(self, id_: str) -> ArticleWithEmbeddings:
        if not await self.index_available():
            raise IndexNotAvailable
        response = await self._client.get(index=self._index_name, id=id_)
        article_document = response["_source"]
        article = await self._document_to_article(article_document)
        return article

    async def search(self, phrase: str) -> List[ArticleWithEmbeddings]:
        if not await self.index_available():
            raise IndexNotAvailable
        raise NotImplemented

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()

    @staticmethod
    async def _document_to_article(document: Dict) -> ArticleWithEmbeddings:
        article = ArticleWithEmbeddings(
            title=document['title'],
            summary=document['summary'],
            content=document['content'],
            title_embed=document['title_embed'],
            summary_embed=document['title_summary'],
            content_embed=document['content_embed']
        )
        return article


def bonsai_elasticsearch(bonsai_url: str, index_name: str = ElasticSearchGateway.DEFAULT_INDEX_NAME):
    return ElasticSearchGateway(BonsaiConfigurator(bonsai_url), index_name=index_name)
