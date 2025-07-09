import warnings
from urllib3.exceptions import InsecureRequestWarning
# 屏蔽 InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

import os
from elasticsearch import Elasticsearch, helpers
import fitz  # PyMuPDF
from tqdm import tqdm
from config import ES_HOST, ES_USERNAME, ES_PASSWORD, ES_INDEX

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

# ========== 3. 解析文档并分段 ==========
def extract_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text(text, chunk_size=500):
    # 按 chunk_size 字符分段
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def parse_and_yield_docs():
    for file_path in DOCS_FILES:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.txt':
            text = extract_txt(file_path)
        elif ext == '.pdf':
            text = extract_pdf(file_path)
        else:
            continue
        doc_name = os.path.basename(file_path)
        chunks = split_text(text)
        for idx, chunk in enumerate(chunks):
            yield {
                '_op_type': 'index',
                '_index': ES_INDEX,
                'doc_name': doc_name,
                'content': chunk,
                'chunk_id': idx
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

