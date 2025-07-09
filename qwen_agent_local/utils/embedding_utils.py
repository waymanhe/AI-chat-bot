import os
from openai import OpenAI
from config import EMBEDDING_MODEL, DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, EMBEDDING_DIM

def get_embedding(text: str, client=None) -> list:
    """用 Dashscope/OpenAI 生成 embedding 向量"""
    if client is None:
        client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL
        )
    if not text.strip():
        return []
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIM,
        encoding_format="float"
    )
    return response.data[0].embedding 