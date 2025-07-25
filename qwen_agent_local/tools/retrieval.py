# Copyright 2023 The Qwen team, Alibaba Group. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Optional, Union

import json5

from qwen_agent_local.settings import DEFAULT_MAX_REF_TOKEN, DEFAULT_PARSER_PAGE_SIZE, DEFAULT_RAG_SEARCHERS
from qwen_agent_local.tools.base import TOOL_REGISTRY, BaseTool, register_tool
from qwen_agent_local.tools.doc_parser import DocParser, Record
from qwen_agent_local.tools.simple_doc_parser import PARSER_SUPPORTED_FILE_TYPES


def _check_deps_for_rag():
    try:
        import charset_normalizer  # noqa
        import jieba  # noqa
        import pdfminer  # noqa
        import pdfplumber  # noqa
        import rank_bm25  # noqa
        import snowballstemmer  # noqa
        from bs4 import BeautifulSoup  # noqa
        from docx import Document  # noqa
        from pptx import Presentation  # noqa
    except ImportError as e:
        raise ImportError('The dependencies for RAG support are not installed. '
                          'Please install the required dependencies by running: pip install "qwen-agent[rag]"') from e


@register_tool('retrieval')
class Retrieval(BaseTool):
    description = f'从给定文件列表中检索出和问题相关的内容，支持文件类型包括：{"/".join(PARSER_SUPPORTED_FILE_TYPES)}'
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': '在这里列出关键词，用逗号分隔，目的是方便在文档中匹配到相关的内容，由于文档可能多语言，关键词最好中英文都有。',
        'required': True
    }, {
        'name': 'files',
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'description': '待解析的文件路径列表，支持本地文件路径或可下载的http(s)链接。',
        'required': True
    }]

    def __init__(self, cfg: Optional[Dict] = None):
        super().__init__(cfg)
        self.max_ref_token: int = self.cfg.get('max_ref_token', DEFAULT_MAX_REF_TOKEN)
        self.parser_page_size: int = self.cfg.get('parser_page_size', DEFAULT_PARSER_PAGE_SIZE)
        self.doc_parse = DocParser({'max_ref_token': self.max_ref_token, 'parser_page_size': self.parser_page_size})

        self.rag_searchers = self.cfg.get('rag_searchers', DEFAULT_RAG_SEARCHERS)
        if len(self.rag_searchers) == 1:
            self.search = TOOL_REGISTRY[self.rag_searchers[0]]({'max_ref_token': self.max_ref_token})
        else:
            from qwen_agent_local.tools.search_tools.hybrid_search import HybridSearch
            self.search = HybridSearch({'max_ref_token': self.max_ref_token, 'rag_searchers': self.rag_searchers})

    def call(self, params: Union[str, dict], **kwargs) -> list:
        """RAG tool.

        Step1: Parse and save files
        Step2: Retrieval related content according to query

        Args:
            params: The files and query.
        Returns:
            The parsed file list or retrieved file list.
        """

        _check_deps_for_rag()

        params = self._verify_json_format_args(params)
        files = params.get('files', [])
        if isinstance(files, str):
            files = json5.loads(files)
        query = params.get('query', '')
        search_type = params.get('search_type', 'hybrid')  # 可选: bm25, embedding, hybrid
        top_k = params.get('top_k', 5)

        # 如有 es_memory，优先用 es 检索
        es_memory = getattr(self, 'es_memory', None)
        memory_type = getattr(self, 'memory_type', 'local')
        if memory_type == 'es' and es_memory is not None:
            if search_type == 'bm25':
                return es_memory.search(query, top_k=top_k)
            elif search_type == 'embedding':
                return es_memory.embedding_search(query, top_k=top_k)
            else:  # 默认 hybrid
                return es_memory.hybrid_search(query, top_k=top_k)

        records = []
        for file in files:
            _record = self.doc_parse.call(params={'url': file}, **kwargs)
            records.append(_record)

        if records:
            return self.search.call(params={'query': query}, docs=[Record(**rec) for rec in records], **kwargs)
        else:
            return []
