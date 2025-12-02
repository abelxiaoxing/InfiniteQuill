# config_manager.py
# -*- coding: utf-8 -*-
import json
import os
import sys
import threading
import platform
from pathlib import Path
from llm_adapters import create_llm_adapter
from embedding_adapters import create_embedding_adapter

# 获取系统配置目录
def get_config_directory() -> Path:
    """
    获取跨平台的用户配置目录
    - Windows: C:/Users/<用户名>/AppData/Local/InfinitQuill/
    - macOS: /Users/<用户名>/Library/Preferences/InfinitQuill/
    - Linux: ~/.config/InfinitQuill/
    """
    system = platform.system()

    if system == "Windows":
        # Windows: 使用 AppData\Local
        config_dir = Path(os.environ.get('APPDATA', '')) / "InfinitQuill"
    elif system == "Darwin":
        # macOS: 使用 Library/Preferences
        home = Path.home()
        config_dir = home / "Library" / "Preferences" / "InfinitQuill"
    else:
        # Linux/Unix: 使用 XDG 规范或 ~/.config
        home = Path.home()
        config_dir = home / ".config" / "InfinitQuill"

    return config_dir

# 获取项目根目录中的默认配置文件路径
def get_default_config_path() -> Path:
    """获取项目根目录中的默认配置文件路径"""
    # 获取当前文件的父目录（即项目根目录）
    current_dir = Path(__file__).parent
    return current_dir / "config.json"

# 获取用户配置文件的实际路径
def get_user_config_path() -> Path:
    """获取用户配置文件的实际存储路径"""
    config_dir = get_config_directory()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config(config_file: str = None) -> dict:
    """
    从指定的 config_file 加载配置，若不存在则创建一个默认配置文件。
    如果未指定config_file，将使用系统用户配置目录。
    首次使用时，如果用户配置目录中不存在配置文件，将从项目目录的config.json复制过来。
    """

    # 如果未指定配置文件路径，使用默认的用户配置路径
    if config_file is None:
        config_file = get_user_config_path()
    else:
        # 如果传入的是相对路径，转换为Path对象处理
        config_file = Path(config_file)

    # 如果用户配置目录中没有配置文件
    if not config_file.exists():
        # 尝试从项目目录复制默认配置
        default_config_path = get_default_config_path()

        if default_config_path.exists():
            # 复制默认配置文件到用户配置目录
            try:
                import shutil
                config_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(default_config_path, config_file)
                print(f"✅ 已将默认配置复制到: {config_file}")
            except Exception as e:
                print(f"⚠️ 复制默认配置失败: {e}")
                # 如果复制失败，创建默认配置
                create_config(str(config_file))
        else:
            # 项目目录中也没有配置文件，创建默认配置
            create_config(str(config_file))

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


# PenBo 增加了创建默认配置文件函数
def create_config(config_file: str) -> dict:
    """创建一个创建默认配置文件。"""
    config = {
    "last_interface_format": "OpenAI",
    "last_embedding_interface_format": "OpenAI",
    "llm_configs": {
        "DeepSeek V3": {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "GPT 5": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-5",
            "temperature": 0.7,
            "max_tokens": 32768,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "Gemini 2.5 Pro": {
            "api_key": "",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model_name": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 32768,
            "timeout": 600,
            "interface_format": "OpenAI"
        }
    },
    "embedding_configs": {
        "OpenAI": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "text-embedding-ada-002",
            "retrieval_k": 4,
            "interface_format": "OpenAI"
        }
    },
    "other_params": {
        "topic": "",
        "genre": "",
        "num_chapters": 0,
        "word_number": 0,
        "filepath": "",
        "chapter_num": "120",
        "user_guidance": "",
        "characters_involved": "",
        "key_items": "",
        "scene_location": "",
        "time_constraint": ""
    },
    "choose_configs": {
        "prompt_draft_llm": "DeepSeek V3",
        "chapter_outline_llm": "DeepSeek V3",
        "architecture_llm": "Gemini 2.5 Pro",
        "final_chapter_llm": "GPT 5",
        "consistency_review_llm": "DeepSeek V3"
    },
    "proxy_setting": {
        "proxy_url": "127.0.0.1",
        "proxy_port": "",
        "enabled": False
    },
    "webdav_config": {
        "webdav_url": "",
        "webdav_username": "",
        "webdav_password": ""
    }
}
    save_config(config, config_file)



def save_config(config_data: dict, config_file: str = None) -> bool:
    """
    将 config_data 保存到 config_file 中，返回 True/False 表示是否成功。
    如果未指定config_file，将使用系统用户配置目录。
    """
    # 如果未指定配置文件路径，使用默认的用户配置路径
    if config_file is None:
        config_file = get_user_config_path()
    else:
        # 如果传入的是相对路径，转换为Path对象处理
        config_file = Path(config_file)

    try:
        # 先加载现有配置（如果存在）
        existing_config = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            except:
                pass  # 如果读取失败，使用空配置
        
        # 合并配置：新配置覆盖旧配置，但保留旧配置中不存在于新配置的字段
        merged_config = existing_config.copy()
        merged_config.update(config_data)
        
        # 确保目录存在
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, ensure_ascii=False, indent=4)
        
        # 添加日志以验证保存内容
        print(f"配置已保存到: {config_file}")
        print(f"保存的配置包含以下键: {list(merged_config.keys())}")
        if "llm_configs" in merged_config:
            print(f"LLM配置已保存，包含 {len(merged_config['llm_configs'])} 个配置")
        
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False

def test_llm_config(interface_format, api_key, base_url, model_name, temperature, max_tokens, timeout, log_func, handle_exception_func):
    """测试当前的LLM配置是否可用"""
    def task():
        try:
            log_func("开始测试LLM配置...")
            llm_adapter = create_llm_adapter(
                interface_format=interface_format,
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            test_prompt = "Please reply 'OK'"
            response = llm_adapter.invoke(test_prompt)
            if response:
                log_func("✅ LLM配置测试成功！")
                log_func(f"测试回复: {response}")
            else:
                log_func("❌ LLM配置测试失败：未获取到响应")
        except Exception as e:
            log_func(f"❌ LLM配置测试出错: {str(e)}")
            handle_exception_func("测试LLM配置时出错")

    threading.Thread(target=task, daemon=True).start()

def test_embedding_config(api_key, base_url, interface_format, model_name, log_func, handle_exception_func):
    """测试当前的Embedding配置是否可用"""
    def task():
        try:
            log_func("开始测试Embedding配置...")
            embedding_adapter = create_embedding_adapter(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )

            test_text = "测试文本"
            embeddings = embedding_adapter.embed_query(test_text)
            if embeddings and len(embeddings) > 0:
                log_func("✅ Embedding配置测试成功！")
                log_func(f"生成的向量维度: {len(embeddings)}")
            else:
                log_func("❌ Embedding配置测试失败：未获取到向量")
        except Exception as e:
            log_func(f"❌ Embedding配置测试出错: {str(e)}")
            handle_exception_func("测试Embedding配置时出错")

    threading.Thread(target=task, daemon=True).start()

def debug_config_save():
    """调试配置保存功能"""
    config_path = get_user_config_path()
    print(f"配置文件路径: {config_path}")
    print(f"配置文件存在: {config_path.exists()}")
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"当前配置包含的键: {list(config.keys())}")
            print(f"是否包含llm_configs: {'llm_configs' in config}")
            if 'llm_configs' in config:
                print(f"LLM配置数量: {len(config['llm_configs'])}")
        except Exception as e:
            print(f"读取配置失败: {e}")