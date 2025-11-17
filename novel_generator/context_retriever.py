#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文检索器 - 专门用于章节上下文连贯性的向量检索模块
实现基于ChromaDB的metadata过滤和相似度匹配
"""
import logging
import traceback
from typing import List, Dict, Optional, Tuple
from .vectorstore_utils import get_relevant_context_from_vector_store


def retrieve_context(embedding_adapter, query: str, filepath: str, chapter_num: int,
                   project_id: str, max_context_tokens: int = 2000, k: int = 3) -> Tuple[str, Dict]:
    """
    检索前章节的相关上下文

    Args:
        embedding_adapter: 嵌入模型适配器
        query: 当前章节的查询文本（蓝图或大纲）
        filepath: 项目文件路径
        chapter_num: 当前章节编号
        project_id: 项目ID
        max_context_tokens: 最大上下文token数
        k: 初始检索段落数

    Returns:
        Tuple[str, Dict]: (格式化的上下文文本, 统计信息)
    """
    logging.info(f"Retrieving context for chapter {chapter_num}, project {project_id}")

    # 如果是第一章，没有前文
    if chapter_num <= 1:
        logging.info("Chapter 1 detected - no previous context available")
        return "", {
            "retrieved": False,
            "reason": "first_chapter",
            "chapter_num": chapter_num,
            "tokens_used": 0,
            "segments_retrieved": 0
        }

    # 检索前一章的内容
    target_chapter = chapter_num - 1

    # 动态调整k值以适应token限制
    current_k = k
    best_context = ""
    best_stats = {}

    while current_k > 0:
        try:
            # 检索前一章的相关内容
            context = get_relevant_context_from_vector_store(
                embedding_adapter=embedding_adapter,
                query=query,
                filepath=filepath,
                k=current_k,
                chapter_num=target_chapter,
                project_id=project_id
            )

            if not context:
                logging.info(f"No context found for chapter {target_chapter}")
                break

            # 计算精确token数
            from .token_utils import calculate_tokens
            estimated_tokens = calculate_tokens(context, "openai", "gpt-3.5-turbo")

            logging.info(f"Retrieved context with k={current_k}: {estimated_tokens:.0f} tokens")

            if estimated_tokens <= max_context_tokens:
                # 找到合适的k值
                best_context = format_context_with_header(context, target_chapter)
                best_stats = {
                    "retrieved": True,
                    "target_chapter": target_chapter,
                    "k_used": current_k,
                    "tokens_used": estimated_tokens,
                    "segments_retrieved": current_k,
                    "similarity_scores": extract_similarity_scores(context)
                }
                logging.info(f"Context retrieved successfully: {estimated_tokens:.0f} tokens, k={current_k}")
                break
            else:
                # 超出token限制，减少k值重试
                logging.info(f"Token limit exceeded ({estimated_tokens:.0f} > {max_context_tokens}), reducing k from {current_k} to {current_k-1}")
                current_k -= 1

        except Exception as e:
            logging.error(f"Error during context retrieval: {e}")
            traceback.print_exc()
            # 如果检索失败，尝试无过滤的检索作为回退
            try:
                logging.info("Attempting fallback retrieval without metadata filter")
                context = get_relevant_context_from_vector_store(
                    embedding_adapter=embedding_adapter,
                    query=query,
                    filepath=filepath,
                    k=current_k,
                    chapter_num=None,
                    project_id=None
                )

                if context:
                    from .token_utils import calculate_tokens
                    estimated_tokens = calculate_tokens(context, "openai", "gpt-3.5-turbo")

                    if estimated_tokens <= max_context_tokens:
                        best_context = format_context_with_header(context, target_chapter)
                        best_stats = {
                            "retrieved": True,
                            "target_chapter": target_chapter,
                            "k_used": current_k,
                            "tokens_used": estimated_tokens,
                            "segments_retrieved": current_k,
                            "similarity_scores": extract_similarity_scores(context),
                            "fallback_used": True
                        }
                        logging.info(f"Fallback retrieval successful: {estimated_tokens:.0f} tokens")
                        break
            except Exception as fallback_e:
                logging.error(f"Fallback retrieval also failed: {fallback_e}")

            break

    if not best_context:
        logging.warning("Failed to retrieve suitable context within token limits")
        return "", {
            "retrieved": False,
            "reason": "token_limit_exceeded",
            "chapter_num": chapter_num,
            "tokens_used": 0,
            "segments_retrieved": 0
        }

    return best_context, best_stats


def format_context_with_header(context: str, source_chapter: int) -> str:
    """
    格式化上下文文本，添加清晰的标题

    Args:
        context: 原始检索到的上下文
        source_chapter: 源章节编号

    Returns:
        str: 格式化后的上下文文本
    """
    formatted = f"""
前文相关信息 (第{source_chapter}章):

{context}

---
"""
    return formatted.strip()


def extract_similarity_scores(context: str) -> List[float]:
    """
    从格式化的上下文中提取相似度分数

    Args:
        context: 格式化的上下文文本

    Returns:
        List[float]: 相似度分数列表
    """
    import re
    pattern = r'\[相似度: (\d+\.\d+)\]'
    matches = re.findall(pattern, context)
    return [float(score) for score in matches]


def validate_context_quality(context: str, min_similarity: float = 0.6) -> Tuple[bool, float]:
    """
    验证检索到的上下文质量

    Args:
        context: 检索到的上下文
        min_similarity: 最低相似度阈值

    Returns:
        Tuple[bool, float]: (是否通过质量检查, 最高相似度分数)
    """
    if not context:
        return False, 0.0

    scores = extract_similarity_scores(context)
    if not scores:
        return False, 0.0

    max_score = max(scores)
    avg_score = sum(scores) / len(scores)

    # 质量标准：最高分数超过阈值，且平均分数合理
    quality_pass = max_score >= min_similarity and avg_score >= min_similarity * 0.7

    logging.info(f"Context quality validation: max_score={max_score:.3f}, avg_score={avg_score:.3f}, pass={quality_pass}")

    return quality_pass, max_score


def generate_project_id(filepath: str) -> str:
    """
    根据文件路径生成唯一的项目ID

    Args:
        filepath: 项目文件路径

    Returns:
        str: 项目ID
    """
    import hashlib
    # 使用路径的哈希值作为项目ID
    project_id = hashlib.md5(filepath.encode()).hexdigest()[:12]
    return f"project_{project_id}"