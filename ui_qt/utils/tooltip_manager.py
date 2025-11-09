# ui_qt/utils/tooltip_manager.py
# -*- coding: utf-8 -*-
"""
工具提示管理器
为应用程序提供统一的工具提示功能
"""

from typing import Dict, Optional
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QFont


class ToolTipManager:
    """工具提示管理器单例"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.tooltips = self._load_tooltips()
            self._initialized = True

    def _load_tooltips(self) -> Dict[str, str]:
        """加载工具提示内容"""
        return {
            # LLM配置相关
            "api_key": "在这里填写你的API Key。如果使用OpenAI官方接口，请在 https://platform.openai.com/account/api-keys 获取。",
            "base_url": "模型的接口地址。若使用OpenAI官方：https://api.openai.com/v1。若使用Ollama本地部署，则类似 http://localhost:11434/v1。调用Gemini模型则无需填写。",
            "interface_format": "指定LLM接口兼容格式，可选DeepSeek、OpenAI、Ollama、ML Studio、Gemini等。\n\n注意：OpenAI兼容是指的可以通过该标准请求的任何接口，不只是api.openai.com。例如Ollama接口格式也兼容OpenAI。",
            "model_name": "要使用的模型名称，例如deepseek-reasoner、gpt-4o等。如果是Ollama等，请填写你下载好的本地模型名。",
            "temperature": "生成文本的随机度。数值越大越具有发散性，越小越严谨。",
            "max_tokens": "限制单次生成的最大Token数。范围1~100000，请根据模型上下文及需求填写合适值。",

            # Embedding配置相关
            "embedding_api_key": "调用Embedding模型时所需的API Key。",
            "embedding_interface_format": "Embedding模型接口风格，比如OpenAI或Ollama。",
            "embedding_url": "Embedding模型接口地址。",
            "embedding_model_name": "Embedding模型名称，如text-embedding-ada-002。",
            "embedding_retrieval_k": "向量检索时返回的Top-K结果数量。",

            # 小说生成相关
            "topic": "小说的大致主题或主要故事背景描述。",
            "genre": "小说的题材类型，如玄幻、都市、科幻等。",
            "num_chapters": "小说期望的章节总数。",
            "word_number": "每章的目标字数。",
            "filepath": "生成文件存储的根目录路径。所有txt文件、向量库等放在该目录下。",
            "chapter_num": "当前正在处理的章节号，用于生成草稿或定稿操作。",
            "user_guidance": "为本章提供的一些额外指令或写作引导。",
            "characters_involved": "本章需要重点描写或影响剧情的角色名单。",
            "key_items": "在本章中出现的重要道具、线索或物品。",
            "scene_location": "本章主要发生的地点或场景描述。",
            "time_constraint": "本章剧情中涉及的时间压力或时限设置。",
            "interface_config": "选择你要使用的AI接口配置。",

            # 新增通用提示
            "webdav_url": "WebDAV服务器地址，格式如：https://your-server.com/remote.php/dav/",
            "webdav_username": "WebDAV服务器用户名",
            "webdav_password": "WebDAV服务器密码",
            "role_name": "角色的名称，建议使用简洁有力的名字",
            "role_age": "角色年龄，可以是具体数字或范围",
            "role_description": "角色的外貌描述和基本特征",
            "personality": "角色的性格特点和心理特征",
            "save_role": "保存当前角色信息到本地文件",
            "new_role": "创建新的角色并清空当前编辑内容",
            "delete_role": "删除当前选中的角色，此操作不可撤销",
            "use_template": "使用预设的角色模板快速创建角色",
            "ai_generate": "使用AI根据描述自动生成角色",
            "import_role": "从外部文件导入角色信息",
            "export_role": "将当前角色导出为文件",
            "copy_role": "复制当前角色为新角色",
            "load_summary": "加载项目全局概览文件(global_summary.txt)",
            "save_summary": "保存项目全局概览文件",
            "insert_template": "插入概览模板到编辑器中",
            "word_count": "当前文本的字数统计",
            "test_connection": "测试与WebDAV服务器的连接是否正常",
            "backup_config": "将当前配置备份到WebDAV云端",
            "restore_config": "从WebDAV云端恢复配置文件",
            "generate_architecture": "生成小说的整体架构，包括世界观、角色设定等",
            "generate_blueprint": "根据架构生成详细的章节目录和大纲",
            "generate_chapter": "生成指定章节的具体内容",
            "consistency_check": "检查当前章节与全局设定的一致性",
        }

    def get_tooltip(self, key: str) -> Optional[str]:
        """获取工具提示内容"""
        return self.tooltips.get(key)

    def add_tooltip(self, widget: QWidget, key: str, delay: int = 500):
        """
        为Widget添加工具提示

        Args:
            widget: 要添加提示的控件
            key: 提示内容的键名
            delay: 显示延迟时间（毫秒）
        """
        tooltip_text = self.get_tooltip(key)
        if not tooltip_text:
            return

        # 设置工具提示
        widget.setToolTip(tooltip_text)

        # 如果是支持hover的控件，可以添加额外的交互
        try:
            # 使用事件过滤来改善工具提示的显示
            widget.installEventFilter(self)
        except:
            pass

    def show_tooltip(self, widget: QWidget, key: str, position: QPoint = None):
        """
        手动显示工具提示

        Args:
            widget: 父控件
            key: 提示内容的键名
            position: 显示位置，如果为None则使用鼠标位置
        """
        tooltip_text = self.get_tooltip(key)
        if not tooltip_text:
            return

        if position is None:
            # 使用鼠标当前位置
            from PySide6.QtGui import QCursor
            position = QCursor.pos()

        QToolTip.showText(position, tooltip_text, widget)

    def eventFilter(self, obj, event):
        """事件过滤器，用于改善工具提示显示"""
        # 可以在这里添加更多交互逻辑
        return super().eventFilter(obj, event)

    def set_global_font(self, font: QFont):
        """设置工具提示的全局字体"""
        QToolTip.setFont(font)

    def add_tooltip_list(self, widget_list: list, key_prefix: str = ""):
        """
        批量为控件添加工具提示

        Args:
            widget_list: 控件列表，元素为(widget, key)元组
            key_prefix: 键名前缀
        """
        for widget, key in widget_list:
            full_key = f"{key_prefix}_{key}" if key_prefix else key
            self.add_tooltip(widget, full_key)


# 全局工具提示管理器实例
tooltip_manager = ToolTipManager()
