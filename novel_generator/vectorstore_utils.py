#novel_generator/vectorstore_utils.py
# -*- coding: utf-8 -*-
"""
向量库相关操作（初始化、更新、检索、清空、文本切分等）
"""
import os
import logging
import traceback
import nltk
import numpy as np
import re
import ssl
import requests
import warnings
import hashlib
from datetime import datetime
from langchain_chroma import Chroma
logging.basicConfig(
    filename='app.log',      # 日志文件名
    filemode='a',            # 追加模式（'w' 会覆盖）
    level=logging.INFO,      # 记录 INFO 及以上级别的日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# 禁用特定的Torch警告
warnings.filterwarnings('ignore', message='.*Torch was not compiled with flash attention.*')
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # 禁用tokenizer并行警告

from chromadb.config import Settings
from langchain.docstore.document import Document
from sklearn.metrics.pairwise import cosine_similarity
from .common import call_with_retry

def get_vectorstore_dir(filepath: str) -> str:
    """获取 vectorstore 路径"""
    return os.path.join(filepath, "vectorstore")

def clear_vector_store(filepath: str) -> bool:
    """清空 清空向量库"""
    import shutil
    store_dir = get_vectorstore_dir(filepath)
    if not os.path.exists(store_dir):
        logging.info("No vector store found to clear.")
        return False
    try:
        shutil.rmtree(store_dir)
        logging.info(f"Vector store directory '{store_dir}' removed.")
        return True
    except Exception as e:
        logging.error(f"无法删除向量库文件夹，请关闭程序后手动删除 {store_dir}。\n {str(e)}")
        traceback.print_exc()
        return False

def init_vector_store(embedding_adapter, texts, filepath: str):
    """
    在 filepath 下创建/加载一个 Chroma 向量库并插入 texts。
    如果Embedding失败，则返回 None，不中断任务。
    """
    from langchain.embeddings.base import Embeddings as LCEmbeddings

    store_dir = get_vectorstore_dir(filepath)
    os.makedirs(store_dir, exist_ok=True)
    documents = [Document(page_content=str(t)) for t in texts]

    try:
        class LCEmbeddingWrapper(LCEmbeddings):
            def embed_documents(self, texts):
                return call_with_retry(
                    func=embedding_adapter.embed_documents,
                    max_retries=3,
                    fallback_return=[],
                    texts=texts
                )
            def embed_query(self, query: str):
                res = call_with_retry(
                    func=embedding_adapter.embed_query,
                    max_retries=3,
                    fallback_return=[],
                    query=query
                )
                return res

        chroma_embedding = LCEmbeddingWrapper()
        vectorstore = Chroma.from_documents(
            documents,
            embedding=chroma_embedding,
            persist_directory=store_dir,
            client_settings=Settings(anonymized_telemetry=False),
            collection_name="novel_collection"
        )
        return vectorstore
    except Exception as e:
        logging.warning(f"Init vector store failed: {e}")
        traceback.print_exc()
        return None

def load_vector_store(embedding_adapter, filepath: str):
    """
    读取已存在的 Chroma 向量库。若不存在则返回 None。
    如果加载失败（embedding 或IO问题），则返回 None。
    """
    from langchain.embeddings.base import Embeddings as LCEmbeddings
    store_dir = get_vectorstore_dir(filepath)
    if not os.path.exists(store_dir):
        logging.info("Vector store not found. Will return None.")
        return None

    try:
        class LCEmbeddingWrapper(LCEmbeddings):
            def embed_documents(self, texts):
                return call_with_retry(
                    func=embedding_adapter.embed_documents,
                    max_retries=3,
                    fallback_return=[],
                    texts=texts
                )
            def embed_query(self, query: str):
                res = call_with_retry(
                    func=embedding_adapter.embed_query,
                    max_retries=3,
                    fallback_return=[],
                    query=query
                )
                return res

        chroma_embedding = LCEmbeddingWrapper()
        return Chroma(
            persist_directory=store_dir,
            embedding_function=chroma_embedding,
            client_settings=Settings(anonymized_telemetry=False),
            collection_name="novel_collection"
        )
    except Exception as e:
        logging.warning(f"Failed to load vector store: {e}")
        traceback.print_exc()
        return None

def split_by_length(text: str, max_length: int = 500):
    """按照 max_length 切分文本"""
    segments = []
    start_idx = 0
    while start_idx < len(text):
        end_idx = min(start_idx + max_length, len(text))
        segment = text[start_idx:end_idx]
        segments.append(segment.strip())
        start_idx = end_idx
    return segments

def split_text_for_vectorstore(chapter_text: str, max_length: int = 500, similarity_threshold: float = 0.7):
    """
    对新的章节文本进行分段后,再用于存入向量库。
    使用 embedding 进行文本相似度计算。
    """
    if not chapter_text.strip():
        return []
    
    # nltk.download('punkt', quiet=True)
    # nltk.download('punkt_tab', quiet=True)
    sentences = nltk.sent_tokenize(chapter_text)
    if not sentences:
        return []
    
    # 直接按长度分段,不做相似度合并
    final_segments = []
    current_segment = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length > max_length:
            if current_segment:
                final_segments.append(" ".join(current_segment))
            current_segment = [sentence]
            current_length = sentence_length
        else:
            current_segment.append(sentence)
            current_length += sentence_length
    
    if current_segment:
        final_segments.append(" ".join(current_segment))
    
    return final_segments

def update_vector_store(embedding_adapter, new_chapter: str, filepath: str, chapter_num: int = None, project_id: str = None):
    """
    将最新章节文本插入到向量库中。
    若库不存在则初始化；若初始化/更新失败，则跳过。

    Args:
        embedding_adapter: 嵌入模型适配器
        new_chapter: 章节文本内容
        filepath: 项目文件路径
        chapter_num: 章节编号（用于metadata）
        project_id: 项目ID（用于metadata）
    """
    from utils import read_file, clear_file_content, save_string_to_txt
    splitted_texts = split_text_for_vectorstore(new_chapter)
    if not splitted_texts:
        logging.warning("No valid text to insert into vector store. Skipping.")
        return

    store = load_vector_store(embedding_adapter, filepath)
    if not store:
        logging.info("Vector store does not exist or failed to load. Initializing a new one for new chapter...")
        store = init_vector_store(embedding_adapter, splitted_texts, filepath)
        if not store:
            logging.warning("Init vector store failed, skip embedding.")
        else:
            logging.info("New vector store created successfully.")
        return

    try:
        # 创建带metadata的文档
        docs = []
        for i, text in enumerate(splitted_texts):
            metadata = {
                "content_type": "full",
                "segment_index": i,
                "timestamp": datetime.now().isoformat()
            }

            # 添加章节和项目metadata（如果提供）
            if chapter_num is not None:
                metadata["chapter_num"] = chapter_num
            if project_id is not None:
                metadata["project_id"] = project_id

            doc = Document(page_content=str(text), metadata=metadata)
            docs.append(doc)

        store.add_documents(docs)
        logging.info(f"Vector store updated with {len(docs)} documents. Chapter: {chapter_num}, Project: {project_id}")
    except Exception as e:
        logging.warning(f"Failed to update vector store: {e}")
        traceback.print_exc()

def get_relevant_context_from_vector_store(embedding_adapter, query: str, filepath: str, k: int = 2,
                                          chapter_num: int = None, project_id: str = None) -> str:
    """
    从向量库中检索与 query 最相关的 k 条文本，拼接后返回。
    如果向量库加载/检索失败，则返回空字符串。
    最终只返回最多2000字符的检索片段。

    Args:
        embedding_adapter: 嵌入模型适配器
        query: 查询文本
        filepath: 项目文件路径
        k: 返回的文档数量
        chapter_num: 过滤特定章节（可选）
        project_id: 过滤特定项目（可选）

    Returns:
        str: 检索到的相关文本拼接结果
    """
    store = load_vector_store(embedding_adapter, filepath)
    if not store:
        logging.info("No vector store found or load failed. Returning empty context.")
        return ""

    try:
        # 构建metadata过滤条件 - ChromaDB需要特定的过滤格式
        filter_dict = None
        if chapter_num is not None or project_id is not None:
            conditions = []
            if chapter_num is not None:
                conditions.append({"chapter_num": chapter_num})
            if project_id is not None:
                conditions.append({"project_id": project_id})

            # 使用$and操作符组合多个条件
            if len(conditions) == 1:
                filter_dict = conditions[0]
            else:
                filter_dict = {"$and": conditions}

        # 使用带分数的相似度搜索
        try:
            if filter_dict:
                docs_with_scores = store.similarity_search_with_score(query, k=k, filter=filter_dict)
            else:
                docs_with_scores = store.similarity_search_with_score(query, k=k)
        except Exception as e:
            # 如果metadata过滤失败，回退到无过滤搜索
            logging.warning(f"Metadata filter failed, falling back to unfiltered search: {e}")
            docs_with_scores = store.similarity_search_with_score(query, k=k)

        if not docs_with_scores:
            logging.info(f"No relevant documents found for query '{query}'. Returning empty context.")
            return ""

        # 格式化结果，包含相似度分数
        combined_parts = []
        total_length = 0
        max_length = 2000

        for doc, score in docs_with_scores:
            text = doc.page_content
            if total_length + len(text) > max_length:
                # 截断最后一段以保持在限制内
                remaining_length = max_length - total_length
                if remaining_length > 50:  # 只在剩余空间足够时才添加
                    text = text[:remaining_length] + "..."
                    combined_parts.append(f"[相似度: {score:.3f}] {text}")
                break

            combined_parts.append(f"[相似度: {score:.3f}] {text}")
            total_length += len(text)

        combined = "\n\n".join(combined_parts)
        logging.info(f"Retrieved {len(docs_with_scores)} documents with metadata filter: {filter_dict}")
        return combined

    except Exception as e:
        logging.warning(f"Similarity search failed: {e}")
        traceback.print_exc()
        return ""

def _get_sentence_transformer(model_name: str = 'paraphrase-MiniLM-L6-v2'):
    """获取sentence transformer模型，处理SSL问题"""
    try:
        # 设置torch环境变量
        os.environ["TORCH_ALLOW_TF32_CUBLAS_OVERRIDE"] = "0"
        os.environ["TORCH_CUDNN_V8_API_ENABLED"] = "0"
        
        # 禁用SSL验证
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # ...existing code...
    except Exception as e:
        logging.error(f"Failed to load sentence transformer model: {e}")
        traceback.print_exc()
        return None
