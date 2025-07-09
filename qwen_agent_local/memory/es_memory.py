import os
from elasticsearch import Elasticsearch, helpers
from config import ES_HOST, ES_USERNAME, ES_PASSWORD, ES_INDEX, ES_EMBEDDING_INDEX, EMBEDDING_DIM
from qwen_agent_local.utils.embedding_utils import get_embedding

class ESMemory:
    """
    用于将文档片段（chunk）存储到 Elasticsearch，并支持高效检索（BM25/embedding/hybrid）。
    """
    def __init__(self, index=ES_INDEX, embedding_index=ES_EMBEDDING_INDEX):
        def ensure_es_port(host):
            if not (host.startswith('http://') or host.startswith('https://')):
                host = 'http://' + host
            host_no_proto = host.split('//', 1)[-1]
            if ':' not in host_no_proto:
                host += ':9200'
            return host
        es_host_with_port = ensure_es_port(ES_HOST)
        self.es = Elasticsearch(
            es_host_with_port,
            basic_auth=(ES_USERNAME, ES_PASSWORD),
            verify_certs=False
        )
        self.index = index
        self.embedding_index = embedding_index
        self.init_index()
        self.init_embedding_index()

    def init_index(self):
        # 创建 BM25 索引（如已存在则跳过）
        if not self.es.indices.exists(index=self.index):
            index_body = {
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "doc_name": {"type": "keyword"},
                        "content": {"type": "text"},
                        "chunk_id": {"type": "integer"}
                    }
                }
            }
            self.es.indices.create(index=self.index, body=index_body)

    def init_embedding_index(self):
        # 创建 embedding 向量索引（如已存在则跳过）
        if not self.es.indices.exists(index=self.embedding_index):
            index_body = {
                "mappings": {
                    "properties": {
                        "doc_name": {"type": "keyword"},
                        "content": {"type": "text"},
                        "content_vector": {
                            "type": "dense_vector",
                            "dims": EMBEDDING_DIM,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "chunk_id": {"type": "integer"}
                    }
                }
            }
            self.es.indices.create(index=self.embedding_index, body=index_body)

    def add_chunks(self, doc_name, chunks):
        """
        批量写入文档片段到 BM25 索引
        :param doc_name: 文档名
        :param chunks: List[str]，每个元素为一个片段
        """
        actions = [
            {
                '_op_type': 'index',
                '_index': self.index,
                'doc_name': doc_name,
                'content': chunk,
                'chunk_id': idx
            }
            for idx, chunk in enumerate(chunks)
        ]
        helpers.bulk(self.es, actions)

    def add_chunks_with_embedding(self, doc_name, chunks, embedding_client=None):
        """
        批量写入文档片段到 embedding 向量索引
        :param doc_name: 文档名
        :param chunks: List[str]，每个元素为一个片段
        """
        actions = []
        for idx, chunk in enumerate(chunks):
            embedding = get_embedding(chunk, client=embedding_client)
            actions.append({
                '_op_type': 'index',
                '_index': self.embedding_index,
                'doc_name': doc_name,
                'content': chunk,
                'content_vector': embedding,
                'chunk_id': idx
            })
        helpers.bulk(self.es, actions)

    def search(self, query, top_k=5):
        """
        BM25 检索最相关的文档片段
        """
        res = self.es.search(index=self.index, query={"match": {"content": query}}, size=top_k)
        return [
            {
                'doc_name': hit['_source']['doc_name'],
                'chunk_id': hit['_source']['chunk_id'],
                'content': hit['_source']['content'],
                'score': hit['_score'],
                'source': 'bm25'
            }
            for hit in res['hits']['hits']
        ]

    def embedding_search(self, query, top_k=5, embedding_client=None):
        """
        embedding 向量检索最相关的文档片段
        """
        query_vector = get_embedding(query, client=embedding_client)
        res = self.es.search(
            index=self.embedding_index,
            knn={
                "field": "content_vector",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": 100
            },
            size=top_k
        )
        return [
            {
                'doc_name': hit['_source']['doc_name'],
                'chunk_id': hit['_source']['chunk_id'],
                'content': hit['_source']['content'],
                'score': hit['_score'],
                'source': 'embedding'
            }
            for hit in res['hits']['hits']
        ]

    def hybrid_search(self, query, top_k=5, embedding_client=None):
        """
        BM25+embedding hybrid 检索，合并去重
        """
        bm25_results = self.search(query, top_k=top_k)
        embedding_results = self.embedding_search(query, top_k=top_k, embedding_client=embedding_client)
        # 合并去重，按分数降序
        all_results = bm25_results + embedding_results
        seen = set()
        merged = []
        for r in sorted(all_results, key=lambda x: x['score'], reverse=True):
            key = (r['doc_name'], r['chunk_id'])
            if key not in seen:
                merged.append(r)
                seen.add(key)
            if len(merged) >= top_k:
                break
        return merged

    def delete_doc(self, doc_name):
        """
        删除指定文档的所有片段
        """
        self.es.delete_by_query(index=self.index, body={"query": {"term": {"doc_name": doc_name}}})
        self.es.delete_by_query(index=self.embedding_index, body={"query": {"term": {"doc_name": doc_name}}}) 