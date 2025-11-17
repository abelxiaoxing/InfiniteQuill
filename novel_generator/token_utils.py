#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token工具模块 - 用于计算和管理LLM token限制
支持多种LLM提供商的token计算
"""
import logging
import re
from typing import Dict, List, Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, using fallback token estimation")


def estimate_tokens_chinese(text: str) -> int:
    """
    估算中文文本的token数量
    使用经验值：中文字符数 * 1.5

    Args:
        text: 中文文本

    Returns:
        int: 估算的token数量
    """
    if not text:
        return 0

    # 移除空白字符，只计算实际内容
    clean_text = re.sub(r'\s+', '', text)
    char_count = len(clean_text)

    # 中文token估算：1个中文字符 ≈ 1.5个token
    # 这个比例是基于OpenAI GPT模型的统计结果
    estimated_tokens = int(char_count * 1.5)

    return estimated_tokens


def calculate_tokens_openai(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    使用tiktoken精确计算OpenAI模型的token数量

    Args:
        text: 文本内容
        model: 模型名称

    Returns:
        int: token数量
    """
    if not TIKTOKEN_AVAILABLE:
        logging.warning("tiktoken not available, using Chinese estimation fallback")
        return estimate_tokens_chinese(text)

    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logging.error(f"Error calculating tokens with tiktoken: {e}")
        return estimate_tokens_chinese(text)


def calculate_tokens_fallback(text: str) -> int:
    """
    通用token估算回退方案

    Args:
        text: 文本内容

    Returns:
        int: 估算的token数量
    """
    if not text:
        return 0

    # 检测文本类型
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    total_chars = len(re.sub(r'\s+', '', text))

    # 混合文本的token估算
    if chinese_chars > total_chars * 0.5:
        # 主要为中文
        return int(chinese_chars * 1.5 + english_words * 1.3)
    else:
        # 主要为英文或其他
        return int(total_chars * 1.2)


def calculate_tokens(text: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> int:
    """
    统一的token计算接口

    Args:
        text: 文本内容
        provider: LLM提供商 ("openai", "anthropic", "cohere" 等)
        model: 模型名称

    Returns:
        int: token数量
    """
    if not text:
        return 0

    provider = provider.lower()

    if provider == "openai" and TIKTOKEN_AVAILABLE:
        return calculate_tokens_openai(text, model)
    else:
        return calculate_tokens_fallback(text)


def truncate_text_by_tokens(text: str, max_tokens: int, provider: str = "openai", model: str = "gpt-3.5-turbo") -> str:
    """
    根据token限制截断文本

    Args:
        text: 原始文本
        max_tokens: 最大token数
        provider: LLM提供商
        model: 模型名称

    Returns:
        str: 截断后的文本
    """
    if not text:
        return ""

    current_tokens = calculate_tokens(text, provider, model)

    if current_tokens <= max_tokens:
        return text

    # 二分查找最佳截断点
    left, right = 0, len(text)
    best_text = ""

    while left <= right:
        mid = (left + right) // 2
        test_text = text[:mid]

        if not test_text:
            break

        test_tokens = calculate_tokens(test_text, provider, model)

        if test_tokens <= max_tokens:
            best_text = test_text
            left = mid + 1
        else:
            right = mid - 1

    # 如果截断点在句子中间，尝试在句号、问号或感叹号处截断
    if best_text and len(best_text) < len(text):
        # 寻找最近的句结束标点
        sentence_endings = ['。', '！', '？', '.', '!', '?']
        for ending in sentence_endings:
            last_pos = best_text.rfind(ending)
            if last_pos > len(best_text) * 0.8:  # 如果句号在文本的80%之后
                best_text = best_text[:last_pos + 1]
                break

    return best_text


def analyze_token_distribution(texts: List[str], provider: str = "openai", model: str = "gpt-3.5-turbo") -> Dict:
    """
    分析文本列表的token分布

    Args:
        texts: 文本列表
        provider: LLM提供商
        model: 模型名称

    Returns:
        Dict: token分布统计信息
    """
    if not texts:
        return {
            "total_tokens": 0,
            "avg_tokens": 0,
            "max_tokens": 0,
            "min_tokens": 0,
            "text_count": 0
        }

    token_counts = [calculate_tokens(text, provider, model) for text in texts]

    return {
        "total_tokens": sum(token_counts),
        "avg_tokens": sum(token_counts) // len(token_counts),
        "max_tokens": max(token_counts),
        "min_tokens": min(token_counts),
        "text_count": len(texts),
        "token_counts": token_counts
    }


def format_token_info(text: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> str:
    """
    格式化token信息用于日志记录

    Args:
        text: 文本内容
        provider: LLM提供商
        model: 模型名称

    Returns:
        str: 格式化的token信息
    """
    if not text:
        return "Empty text - 0 tokens"

    tokens = calculate_tokens(text, provider, model)
    chars = len(text)
    chars_no_space = len(re.sub(r'\s+', '', text))

    ratio = tokens / chars_no_space if chars_no_space > 0 else 0

    return f"Tokens: {tokens}, Characters: {chars}, Ratio: {ratio:.2f}"


class TokenManager:
    """
    Token管理器，用于跟踪和管理token使用情况
    """
    def __init__(self, max_tokens: int = 2000, provider: str = "openai", model: str = "gpt-3.5-turbo"):
        self.max_tokens = max_tokens
        self.provider = provider
        self.model = model
        self.used_tokens = 0
        self.texts = []

    def add_text(self, text: str) -> bool:
        """
        添加文本，检查是否超出token限制

        Args:
            text: 要添加的文本

        Returns:
            bool: 是否成功添加（未超出限制）
        """
        tokens = calculate_tokens(text, self.provider, self.model)

        if self.used_tokens + tokens > self.max_tokens:
            return False

        self.used_tokens += tokens
        self.texts.append(text)
        return True

    def get_remaining_tokens(self) -> int:
        """获取剩余token数"""
        return max(0, self.max_tokens - self.used_tokens)

    def get_usage_ratio(self) -> float:
        """获取token使用率"""
        return self.used_tokens / self.max_tokens if self.max_tokens > 0 else 0

    def reset(self):
        """重置管理器状态"""
        self.used_tokens = 0
        self.texts = []

    def get_combined_text(self) -> str:
        """获取所有文本的组合"""
        return "\n".join(self.texts)

    def __str__(self) -> str:
        return f"TokenManager(used={self.used_tokens}, max={self.max_tokens}, ratio={self.get_usage_ratio():.2%})"