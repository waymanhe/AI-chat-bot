import warnings
from urllib3.exceptions import InsecureRequestWarning
# 屏蔽 InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

import os
from elasticsearch import Elasticsearch, helpers
import fitz  # PyMuPDF
from tqdm import tqdm
from config import ES_HOST, ES_USERNAME, ES_PASSWORD, ES_INDEX, MINERU_API_KEY
import json

# ========== 自动获取 docs 目录下所有文件 ==========
DOCS_DIR = './docs'
DOCS_FILES = []
if os.path.exists(DOCS_DIR):
    for file in os.listdir(DOCS_DIR):
        file_path = os.path.join(DOCS_DIR, file)
        if os.path.isfile(file_path):
            DOCS_FILES.append(file_path)

print(f"找到 {len(DOCS_FILES)} 个文件: {DOCS_FILES}")

# ========== 1. 连接到 Elasticsearch ==========
# 自动拼接端口:9200（如未指定）
def ensure_es_port(host):
    # 检查是否已带端口
    host_no_proto = host.split('//', 1)[-1]
    if ':' not in host_no_proto:
        host += ':9200'
    return host

es_host_with_port = ensure_es_port(ES_HOST)

es = Elasticsearch(
    es_host_with_port,
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False  # 若为自签证书可设为False
)

# ========== 2. 创建索引（如已存在则跳过） ==========
index_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "doc_name": {"type": "keyword"},
            "content": {"type": "text"},
            "chunk_id": {"type": "integer"}
        }
    }
}
if not es.indices.exists(index=ES_INDEX):
    es.indices.create(index=ES_INDEX, body=index_body)
    print(f"已创建索引: {ES_INDEX}")
else:
    print(f"索引已存在: {ES_INDEX}")

# ========== 3. 解析 minerU 结构化 JSON 并分段 ==========
PROCESSED_DIR = './processed_reports'

def parse_mineru_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    texts = []
    if isinstance(data, dict):
        if 'pages' in data:
            for page in data['pages']:
                txt = page.get('text', '')
                if txt.strip():
                    texts.append(txt)
        elif 'paragraphs' in data:
            for para in data['paragraphs']:
                txt = para.get('text', '')
                if txt.strip():
                    texts.append(txt)
        elif 'content' in data and isinstance(data['content'], str):
            if data['content'].strip():
                texts.append(data['content'])
        else:
            print(f"[警告] {json_path} 结构异常，未能提取文本。")
    elif isinstance(data, list):
        for page in data:
            txt = page.get('text', '')
            if txt.strip():
                texts.append(txt)
    else:
        print(f"[警告] {json_path} 结构异常，未能提取文本。")
    return texts

def split_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def parse_and_yield_docs():
    for fname in os.listdir(PROCESSED_DIR):
        if fname.endswith('.json'):
            doc_name = fname.replace('.json', '')
            texts = parse_mineru_json(os.path.join(PROCESSED_DIR, fname))
            for idx, chunk in enumerate(texts):
                for sub_idx, sub_chunk in enumerate(split_text(chunk)):
                    if not sub_chunk.strip():
                        continue
                    yield {
                        '_op_type': 'index',
                        '_index': ES_INDEX,
                        'doc_name': doc_name,
                        'content': sub_chunk,
                        'chunk_id': idx * 10000 + sub_idx  # 保证唯一且为整数
                    }

# ========== 4. 批量写入ES ==========
print("正在写入文档到ES...")
helpers.bulk(es, parse_and_yield_docs())
print("写入完成！")

# ========== 5. 执行搜索 ========== 
# 为了测试一下是否转换成功 size返回最接近的前三个
search_query = "中石化研学活动守则有哪些？"
rep_size = 3
print(f"\n搜索: {search_query}")
response = es.search(index=ES_INDEX, query={"match": {"content": search_query}}, size=rep_size)

print("\n--- 搜索结果 ---")
hits = response['hits']['hits']
if not hits:
    print("没有找到匹配的文档。")
else:
    for i, hit in enumerate(hits):
        print(f"\n--- 结果 {i+1} ---")
        print(f"来源文件: {hit['_source'].get('doc_name', hit['_source'].get('file_name', '未知'))}")
        print(f"相关度得分: {hit['_score']:.2f}")
        content_preview = hit['_source']['content'].strip().replace('\n', ' ')
        print(f"内容预览: {content_preview[:200]}...")

