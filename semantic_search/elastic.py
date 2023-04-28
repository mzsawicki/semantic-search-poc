from abc import ABCMeta, abstractmethod
from dataclasses import asdict
from typing import List, Dict

from elasticsearch import AsyncElasticsearch

from semantic_search.boost import Boost
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


class ElasticCloudConfigurator(ElasticSearchConfigurator):
    def __init__(self, cloud_id: str, user: str, password: str):
        self._cloud_id = cloud_id
        self._user = user
        self._password = password

    def configure_client(self) -> AsyncElasticsearch:
        client = AsyncElasticsearch(cloud_id=self._cloud_id, basic_auth=(self._user, self._password))
        return client


class ElasticsearchLocalConfigurator(ElasticSearchConfigurator):
    """For local / docker deployments of Elasticsearch"""
    def __init__(self, hosts: str, user: str, password: str):
        self._hosts = hosts.split(',')
        self._user = user
        self._password = password

    def configure_client(self) -> AsyncElasticsearch:
        client = AsyncElasticsearch(hosts=self._hosts, basic_auth=(self._user, self._password))
        return client


class ElasticSearchGateway:
    DEFAULT_INDEX_NAME = 'articles'
    SEARCH_FUZZINESS = 0    # max 6 for Levenshtein distance <= 2
    KNN_PARAMETER_K = 5
    KNN_PARAMETER_NUM_CANDIDATES = 10

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
        return response['_id']

    async def find_article_by_id(self, id_: str) -> ArticleWithEmbeddings:
        if not await self.index_available():
            raise IndexNotAvailable
        response = await self._client.get(index=self._index_name, id=id_)
        article_document = response['_source']
        article = self._document_to_article(article_document)
        return article

    async def search(self, phrase: str, phrase_embed: List[float] = None) -> List[Dict]:
        if not await self.index_available():
            raise IndexNotAvailable
        query = {
            'multi_match': {
                'query': phrase,
                'fields': [
                    f'title^{Boost.title}',
                    f'summary^{Boost.summary}',
                    f'content^{Boost.content}'
                ],
                'fuzziness': self.SEARCH_FUZZINESS
            }
        }
        knn = None
        if phrase_embed:
            knn = [
                {
                    'field': 'title_embed',
                    'query_vector': phrase_embed,
                    'k': self.KNN_PARAMETER_K,
                    'num_candidates': self.KNN_PARAMETER_NUM_CANDIDATES,
                    'boost': Boost.title_embed
                },
                {
                    'field': 'summary_embed',
                    'query_vector': phrase_embed,
                    'k': self.KNN_PARAMETER_K,
                    'num_candidates': self.KNN_PARAMETER_NUM_CANDIDATES,
                    'boost': Boost.summary_embed
                },
                {
                    'field': 'content_embed',
                    'query_vector': phrase_embed,
                    'k': self.KNN_PARAMETER_K,
                    'num_candidates': self.KNN_PARAMETER_NUM_CANDIDATES,
                    'boost': Boost.content_embed
                },
            ]
        response = await self._client.search(query=query, knn=knn, source_excludes='*embed')

        hits = response.body['hits']['hits']
        if not hits:
            return list()

        entries = [hit['_source'] for hit in response.body['hits']['hits']]
        return entries

    async def close(self):
        await self._client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @staticmethod
    def _document_to_article(document: Dict) -> ArticleWithEmbeddings:
        article = ArticleWithEmbeddings(
            title=document['title'],
            summary=document['summary'],
            content=document['content'],
            title_embed=document['title_embed'],
            summary_embed=document['summary_embed'],
            content_embed=document['content_embed']
        )
        return article


def elastic_cloud(cloud_id: str,  user: str, password: str, index_name: str = ElasticSearchGateway.DEFAULT_INDEX_NAME):
    return ElasticSearchGateway(ElasticCloudConfigurator(cloud_id, user, password), index_name=index_name)


def elasticsearch_local(hosts_string: str, user: str, password: str,
                        index_name: str = ElasticSearchGateway.DEFAULT_INDEX_NAME):
    return ElasticSearchGateway(ElasticsearchLocalConfigurator(hosts_string, user, password), index_name=index_name)
