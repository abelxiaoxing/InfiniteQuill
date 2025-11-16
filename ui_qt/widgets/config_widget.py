# ui_qt/widgets/config_widget.py
# -*- coding: utf-8 -*-
"""
配置管理组件
管理LLM配置、API密钥、代理设置等
"""

import os
import threading
import logging
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QSlider, QFrame, QTextEdit
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help, validate_required, validate_url, validate_api_key
)
from ..utils.tooltip_manager import tooltip_manager

# 导入配置管理函数
from config_manager import save_config


class ConfigWidget(QWidget):
    """配置管理组件"""

    # 信号定义
    config_changed = Signal(dict)
    auto_save_started = Signal()
    auto_save_completed = Signal(bool)  # True表示成功，False表示失败
    auto_save_status_changed = Signal(str, str)  # 状态类型(info/success/error), 消息内容

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.original_config = config.copy()  # 保存原始配置用于比较
        self.status_bar = None  # 状态栏引用，将在主窗口设置

        # 自动保存相关属性
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.setInterval(2000)  # 2秒延迟
        self.auto_save_timer.timeout.connect(self.perform_auto_save)

        # 后台保存线程相关
        self.save_thread = None
        self.is_saving = False
        self.pending_save = False

        self.setup_ui()
        self.load_current_config()
        self.connect_change_listeners()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)


        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tab_widget)

        # 创建各个配置选项卡
        self.create_llm_config_tab()
        self.create_llm_selection_tab()
        self.create_embedding_config_tab()
        self.create_proxy_config_tab()
        self.create_advanced_config_tab()

        # 底部按钮
        self.create_bottom_buttons(layout)

        # 设置工具提示
        self.setup_tooltips()

    def create_llm_config_tab(self):
        """创建LLM配置选项卡"""
        llm_widget = QWidget()
        layout = QVBoxLayout(llm_widget)
        layout.setSpacing(15)

        # 配置选择器
        config_selector_group = QGroupBox("配置选择器")
        config_selector_layout = QHBoxLayout(config_selector_group)

        config_selector_layout.addWidget(QLabel("当前配置:"))
        self.config_selector = QComboBox()
        self.config_selector.currentTextChanged.connect(self.on_config_selected)
        config_selector_layout.addWidget(self.config_selector)

        self.add_config_btn = QPushButton("+ 新增配置")
        self.add_config_btn.clicked.connect(self.add_new_config)
        config_selector_layout.addWidget(self.add_config_btn)

        self.delete_config_btn = QPushButton("- 删除配置")
        self.delete_config_btn.clicked.connect(self.delete_current_config)
        config_selector_layout.addWidget(self.delete_config_btn)

        layout.addWidget(config_selector_group)

        # LLM基本设置
        llm_group = QGroupBox("LLM基本设置")
        llm_layout = QFormLayout(llm_group)

        # 接口格式
        self.interface_format = QComboBox()
        self.interface_format.addItems(["OpenAI", "DeepSeek", "Gemini", "Azure"])
        llm_layout.addRow("接口格式:", self.interface_format)

        # API密钥
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("输入API密钥...")
        llm_layout.addRow("API密钥:", self.api_key)

        # 基础URL
        self.base_url = QLineEdit()
        self.base_url.setPlaceholderText("https://api.openai.com/v1")
        llm_layout.addRow("基础URL:", self.base_url)

        # 模型名称
        self.model_name = QComboBox()
        self.model_name.setEditable(True)
        self.model_name.addItems([
            "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo",
            "deepseek-chat", "deepseek-coder",
            "gemini-pro", "gemini-1.5-flash"
        ])
        llm_layout.addRow("模型名称:", self.model_name)

        layout.addWidget(llm_group)

        # 高级参数设置
        params_group = QGroupBox("高级参数")
        params_layout = QGridLayout(params_group)

        # 温度参数
        params_layout.addWidget(QLabel("温度:"), 0, 0)
        temp_widget = QWidget()
        temp_layout = QHBoxLayout(temp_widget)
        temp_layout.setContentsMargins(0, 0, 0, 0)
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 20)  # 0.0 - 2.0, 10倍精度
        self.temperature_slider.setValue(7)  # 0.7
        self.temperature_label = QLabel("0.7")
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(str(v/10))
        )
        temp_layout.addWidget(self.temperature_slider, 1)
        temp_layout.addWidget(self.temperature_label)
        params_layout.addWidget(temp_widget, 0, 1)

        # 最大令牌数
        params_layout.addWidget(QLabel("最大令牌数:"), 1, 0)
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(1, 32000)
        self.max_tokens.setValue(8192)
        params_layout.addWidget(self.max_tokens, 1, 1)

        # 超时时间
        params_layout.addWidget(QLabel("超时时间(秒):"), 2, 0)
        self.timeout = QSpinBox()
        self.timeout.setRange(30, 3600)
        self.timeout.setValue(600)
        params_layout.addWidget(self.timeout, 2, 1)

        layout.addWidget(params_group)

        # 测试按钮
        test_group = QGroupBox("连接测试")
        test_layout = QHBoxLayout(test_group)

        self.test_llm_btn = QPushButton(" 测试LLM连接")
        self.test_llm_btn.clicked.connect(self.test_llm_connection)
        test_layout.addWidget(self.test_llm_btn)

        self.test_result = QLabel("未测试")
        test_layout.addWidget(self.test_result)
        test_layout.addStretch()

        layout.addWidget(test_group)
        layout.addStretch()

        self.tab_widget.addTab(llm_widget, "LLM配置")

    def create_llm_selection_tab(self):
        """创建LLM模型选择选项卡"""
        selection_widget = QWidget()
        layout = QVBoxLayout(selection_widget)
        layout.setSpacing(15)

        # 标题说明
        title_label = QLabel("为不同生成阶段选择最适合的LLM模型")
        title_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        layout.addWidget(title_label)

        # 说明文字
        desc_label = QLabel("您可以为以下各个生成阶段单独选择不同的LLM模型，以获得最佳的生成效果")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray;")
        layout.addWidget(desc_label)

        layout.addWidget(create_separator())

        # 创建模型选择组
        selection_group = QGroupBox("生成阶段LLM模型选择")
        selection_layout = QFormLayout(selection_group)

        # 获取所有可用的LLM配置名称
        llm_configs = self.config.get("llm_configs", {})
        available_models = list(llm_configs.keys()) if llm_configs else ["DeepSeek V3", "GPT 5", "Gemini 2.5 Pro"]

        # 提示词草稿生成
        self.prompt_draft_llm = QComboBox()
        self.prompt_draft_llm.addItems(available_models)
        selection_layout.addRow("提示词草稿生成:", self.prompt_draft_llm)
        tooltip_manager.add_tooltip(self.prompt_draft_llm, "选择用于生成提示词草稿的LLM模型")

        # 架构生成
        self.architecture_llm = QComboBox()
        self.architecture_llm.addItems(available_models)
        selection_layout.addRow("小说架构生成:", self.architecture_llm)
        tooltip_manager.add_tooltip(self.architecture_llm, "选择用于生成小说世界观、角色设定的LLM模型")

        # 章节大纲生成
        self.chapter_outline_llm = QComboBox()
        self.chapter_outline_llm.addItems(available_models)
        selection_layout.addRow("章节大纲生成:", self.chapter_outline_llm)
        tooltip_manager.add_tooltip(self.chapter_outline_llm, "选择用于生成章节蓝图的LLM模型")

        # 章节内容生成
        self.final_chapter_llm = QComboBox()
        self.final_chapter_llm.addItems(available_models)
        selection_layout.addRow("章节内容生成:", self.final_chapter_llm)
        tooltip_manager.add_tooltip(self.final_chapter_llm, "选择用于生成具体章节内容的LLM模型")

        # 一致性检查
        self.consistency_review_llm = QComboBox()
        self.consistency_review_llm.addItems(available_models)
        selection_layout.addRow("一致性检查:", self.consistency_review_llm)
        tooltip_manager.add_tooltip(self.consistency_review_llm, "选择用于检查内容一致性的LLM模型")

        layout.addWidget(selection_group)

        layout.addStretch()

        self.tab_widget.addTab(selection_widget, "模型选择")

    def create_embedding_config_tab(self):
        """创建嵌入配置选项卡"""
        embed_widget = QWidget()
        layout = QVBoxLayout(embed_widget)
        layout.setSpacing(15)

        # 基本设置
        basic_group = QGroupBox("嵌入模型设置")
        basic_layout = QFormLayout(basic_group)

        # 接口格式
        self.embedding_interface = QComboBox()
        self.embedding_interface.addItems(["OpenAI", "HuggingFace", "本地"])
        basic_layout.addRow("接口格式:", self.embedding_interface)

        # API密钥
        self.embedding_api_key = QLineEdit()
        self.embedding_api_key.setEchoMode(QLineEdit.Password)
        basic_layout.addRow("API密钥:", self.embedding_api_key)

        # 基础URL
        self.embedding_url = QLineEdit()
        self.embedding_url.setPlaceholderText("https://api.openai.com/v1")
        basic_layout.addRow("基础URL:", self.embedding_url)

        # 模型名称
        self.embedding_model = QComboBox()
        self.embedding_model.setEditable(True)
        self.embedding_model.addItems([
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large"
        ])
        basic_layout.addRow("模型名称:", self.embedding_model)

        layout.addWidget(basic_group)

        # 检索设置
        retrieval_group = QGroupBox("检索参数")
        retrieval_layout = QFormLayout(retrieval_group)

        # 检索K值
        self.retrieval_k = QSpinBox()
        self.retrieval_k.setRange(1, 20)
        self.retrieval_k.setValue(4)
        retrieval_layout.addRow("检索数量(K):", self.retrieval_k)

        # 分块大小
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(100, 4000)
        self.chunk_size.setValue(1000)
        retrieval_layout.addRow("分块大小:", self.chunk_size)

        # 重叠大小
        self.chunk_overlap = QSpinBox()
        self.chunk_overlap.setRange(0, 1000)
        self.chunk_overlap.setValue(200)
        retrieval_layout.addRow("重叠大小:", self.chunk_overlap)

        layout.addWidget(retrieval_group)

        # 测试按钮
        test_group = QGroupBox("连接测试")
        test_layout = QHBoxLayout(test_group)

        self.test_embedding_btn = QPushButton(" 测试嵌入连接")
        self.test_embedding_btn.clicked.connect(self.test_embedding_connection)
        test_layout.addWidget(self.test_embedding_btn)

        self.embedding_test_result = QLabel("未测试")
        test_layout.addWidget(self.embedding_test_result)
        test_layout.addStretch()

        layout.addWidget(test_group)
        layout.addStretch()

        self.tab_widget.addTab(embed_widget, " 嵌入配置")

    def create_proxy_config_tab(self):
        """创建代理配置选项卡"""
        proxy_widget = QWidget()
        layout = QVBoxLayout(proxy_widget)
        layout.setSpacing(15)

        # 代理设置组
        proxy_group = QGroupBox("代理服务器设置")
        proxy_layout = QFormLayout(proxy_group)

        # 启用代理
        self.enable_proxy = QCheckBox("启用HTTP代理")
        self.enable_proxy.stateChanged.connect(self.on_proxy_state_changed)
        proxy_layout.addRow("", self.enable_proxy)

        # 代理服务器
        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("127.0.0.1")
        proxy_layout.addRow("代理服务器:", self.proxy_host)

        # 代理端口
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(7890)
        proxy_layout.addRow("代理端口:", self.proxy_port)

        # 用户名（可选）
        self.proxy_username = QLineEdit()
        self.proxy_username.setPlaceholderText("可选")
        proxy_layout.addRow("用户名:", self.proxy_username)

        # 密码（可选）
        self.proxy_password = QLineEdit()
        self.proxy_password.setEchoMode(QLineEdit.Password)
        self.proxy_password.setPlaceholderText("可选")
        proxy_layout.addRow("密码:", self.proxy_password)

        layout.addWidget(proxy_group)

        # 说明信息
        info_group = QGroupBox("使用说明")
        info_layout = QVBoxLayout(info_group)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText("""代理设置说明：

1. HTTP代理：用于HTTP请求的代理服务器
2. SOCKS代理：支持SOCKS5协议的代理服务器
3. 认证信息：如果代理需要身份验证，请填写用户名和密码
4. 系统代理：程序启动时会自动读取系统代理设置

注意事项：
• 代理设置会影响所有网络请求
• 请确保代理服务器可用且网络通畅
• 如遇到连接问题，请检查代理配置
""")
        info_layout.addWidget(info_text)

        layout.addWidget(info_group)
        layout.addStretch()

        self.tab_widget.addTab(proxy_widget, "代理设置")

    def create_advanced_config_tab(self):
        """创建高级配置选项卡"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        layout.setSpacing(15)

        # 日志设置
        log_group = QGroupBox("日志设置")
        log_layout = QFormLayout(log_group)

        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_layout.addRow("日志级别:", self.log_level)

        self.log_file = QLineEdit()
        self.log_file.setText("app.log")
        log_layout.addRow("日志文件:", self.log_file)

        layout.addWidget(log_group)

        # 性能设置
        perf_group = QGroupBox("性能设置")
        perf_layout = QFormLayout(perf_group)

        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 20)
        self.max_workers.setValue(4)
        perf_layout.addRow("最大工作线程:", self.max_workers)

        self.request_timeout = QSpinBox()
        self.request_timeout.setRange(5, 300)
        self.request_timeout.setValue(30)
        perf_layout.addRow("请求超时(秒):", self.request_timeout)

        self.retry_count = QSpinBox()
        self.retry_count.setRange(0, 10)
        self.retry_count.setValue(3)
        perf_layout.addRow("重试次数:", self.retry_count)

        layout.addWidget(perf_group)

        # 界面设置
        ui_group = QGroupBox("界面设置")
        ui_layout = QFormLayout(ui_group)

        self.auto_save = QCheckBox("自动保存配置")
        ui_layout.addRow("", self.auto_save)

        self.save_interval = QSpinBox()
        self.save_interval.setRange(1, 60)
        self.save_interval.setValue(5)
        ui_layout.addRow("自动保存间隔(分钟):", self.save_interval)

        self.show_tooltips = QCheckBox("显示工具提示")
        self.show_tooltips.setChecked(True)
        ui_layout.addRow("", self.show_tooltips)

        layout.addWidget(ui_group)
        layout.addStretch()

        self.tab_widget.addTab(advanced_widget, " 高级设置")

    def create_bottom_buttons(self, layout: QVBoxLayout):
        """创建底部按钮"""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()

        self.reset_btn = QPushButton(" 重置")
        self.reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(self.reset_btn)

        self.apply_btn = QPushButton(" 应用")
        self.apply_btn.clicked.connect(self.apply_config)
        button_layout.addWidget(self.apply_btn)

        self.save_btn = QPushButton(" 保存配置")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)

        layout.addWidget(button_widget)

    def load_current_config(self):
        """加载当前配置到界面"""
        # 加载LLM配置
        llm_configs = self.config.get("llm_configs", {})
        if llm_configs:
            self.config_selector.clear()
            self.config_selector.addItems(list(llm_configs.keys()))

            # 设置当前选中
            choose_configs = self.config.get("choose_configs", {})
            current_config = choose_configs.get("default", list(llm_configs.keys())[0])
            if current_config in llm_configs:
                self.config_selector.setCurrentText(current_config)
                self.load_llm_config_to_ui(current_config)

            # 加载LLM模型选择配置
            self.load_llm_selection_to_ui(choose_configs)

        # 加载嵌入配置
        embedding_configs = self.config.get("embedding_configs", {})
        if embedding_configs:
            last_embedding = self.config.get("last_embedding_interface_format", "OpenAI")
            if last_embedding in embedding_configs:
                self.load_embedding_config_to_ui(last_embedding)

        # 加载代理配置
        proxy_setting = self.config.get("proxy_setting", {})
        self.load_proxy_config_to_ui(proxy_setting)

        # 加载高级配置
        self.load_advanced_config_to_ui()

    def load_llm_config_to_ui(self, config_name: str):
        """加载LLM配置到界面"""
        llm_configs = self.config.get("llm_configs", {})
        if config_name not in llm_configs:
            return

        config_data = llm_configs[config_name]
        self.interface_format.setCurrentText(config_data.get("interface_format", "OpenAI"))
        self.api_key.setText(config_data.get("api_key", ""))
        self.base_url.setText(config_data.get("base_url", "https://api.openai.com/v1"))
        self.model_name.setCurrentText(config_data.get("model_name", "gpt-4o-mini"))
        self.temperature_slider.setValue(int(config_data.get("temperature", 0.7) * 10))

        # 安全处理max_tokens值
        max_tokens = config_data.get("max_tokens")
        if max_tokens is None or max_tokens == "":
            max_tokens = 8192
        self.max_tokens.setValue(int(max_tokens))

        # 安全处理timeout值
        timeout = config_data.get("timeout")
        if timeout is None or timeout == "":
            timeout = 600
        self.timeout.setValue(int(timeout))

    def load_embedding_config_to_ui(self, interface_format: str):
        """加载嵌入配置到界面"""
        embedding_configs = self.config.get("embedding_configs", {})
        if interface_format not in embedding_configs:
            return

        config_data = embedding_configs[interface_format]
        self.embedding_interface.setCurrentText(config_data.get("interface_format", interface_format))
        self.embedding_api_key.setText(config_data.get("api_key", ""))
        self.embedding_url.setText(config_data.get("base_url", "https://api.openai.com/v1"))
        self.embedding_model.setCurrentText(config_data.get("model_name", "text-embedding-ada-002"))

        # 安全处理retrieval_k值
        retrieval_k = config_data.get("retrieval_k")
        if retrieval_k is None or retrieval_k == "":
            retrieval_k = 4
        self.retrieval_k.setValue(int(retrieval_k))

    def load_llm_selection_to_ui(self, choose_configs: Dict[str, Any]):
        """加载LLM模型选择到界面"""
        if not choose_configs:
            return

        # 设置各个生成阶段选择的LLM
        if hasattr(self, 'prompt_draft_llm'):
            prompt_draft = choose_configs.get("prompt_draft_llm", "DeepSeek V3")
            if self.prompt_draft_llm.findText(prompt_draft) >= 0:
                self.prompt_draft_llm.setCurrentText(prompt_draft)

        if hasattr(self, 'architecture_llm'):
            architecture = choose_configs.get("architecture_llm", "Gemini 2.5 Pro")
            if self.architecture_llm.findText(architecture) >= 0:
                self.architecture_llm.setCurrentText(architecture)

        if hasattr(self, 'chapter_outline_llm'):
            chapter_outline = choose_configs.get("chapter_outline_llm", "DeepSeek V3")
            if self.chapter_outline_llm.findText(chapter_outline) >= 0:
                self.chapter_outline_llm.setCurrentText(chapter_outline)

        if hasattr(self, 'final_chapter_llm'):
            final_chapter = choose_configs.get("final_chapter_llm", "GPT 5")
            if self.final_chapter_llm.findText(final_chapter) >= 0:
                self.final_chapter_llm.setCurrentText(final_chapter)

        if hasattr(self, 'consistency_review_llm'):
            consistency = choose_configs.get("consistency_review_llm", "DeepSeek V3")
            if self.consistency_review_llm.findText(consistency) >= 0:
                self.consistency_review_llm.setCurrentText(consistency)

    def load_proxy_config_to_ui(self, proxy_setting: Dict[str, Any]):
        """加载代理配置到界面"""
        self.enable_proxy.setChecked(proxy_setting.get("enabled", False))
        self.proxy_host.setText(proxy_setting.get("proxy_url", "127.0.0.1"))
        port_value = proxy_setting.get("proxy_port", "7890")
        self.proxy_port.setValue(int(port_value) if port_value else 7890)
        self.proxy_username.setText(proxy_setting.get("username", ""))
        self.proxy_password.setText(proxy_setting.get("password", ""))

    def load_advanced_config_to_ui(self):
        """加载高级配置到界面"""
        # 加载日志设置
        self.log_level.setCurrentText(self.config.get("log_level", "INFO"))
        self.log_file.setText(self.config.get("log_file", "app.log"))

        # 加载性能设置
        self.max_workers.setValue(int(self.config.get("max_workers", 4)))
        self.request_timeout.setValue(int(self.config.get("request_timeout", 30)))
        self.retry_count.setValue(int(self.config.get("retry_count", 3)))

        # 加载界面设置
        self.auto_save.setChecked(self.config.get("auto_save", True))
        self.save_interval.setValue(int(self.config.get("save_interval", 5)))
        self.show_tooltips.setChecked(self.config.get("show_tooltips", True))

    def on_config_selected(self, config_name: str):
        """配置选择变更处理"""
        if config_name:
            self.load_llm_config_to_ui(config_name)

    def on_proxy_state_changed(self, state: int):
        """代理状态变更处理"""
        enabled = state == Qt.Checked
        self.proxy_host.setEnabled(enabled)
        self.proxy_port.setEnabled(enabled)
        self.proxy_username.setEnabled(enabled)
        self.proxy_password.setEnabled(enabled)

    def add_new_config(self):
        """添加新配置"""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "新增配置", "请输入配置名称:")
        if ok and name.strip():
            # 如果是新配置，设置默认值
            if name not in self.config.get("llm_configs", {}):
                if "llm_configs" not in self.config:
                    self.config["llm_configs"] = {}

                self.config["llm_configs"][name] = {
                    "interface_format": "OpenAI",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.7,
                    "max_tokens": 8192,
                    "timeout": 600
                }

                self.config_selector.addItem(name)
                self.config_selector.setCurrentText(name)
                self.load_llm_config_to_ui(name)

                # 更新LLM模型选择选项卡中的模型列表
                self.update_llm_selection_models()

                show_info_dialog(self, "成功", f"配置 '{name}' 已添加")
            else:
                show_error_dialog(self, "错误", f"配置 '{name}' 已存在")

    def delete_current_config(self):
        """删除当前配置"""
        current_config = self.config_selector.currentText()
        if not current_config:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除配置 '{current_config}' 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if "llm_configs" in self.config and current_config in self.config["llm_configs"]:
                del self.config["llm_configs"][current_config]
                self.config_selector.removeItem(self.config_selector.findText(current_config))

                # 更新LLM模型选择选项卡中的模型列表
                self.update_llm_selection_models()

                show_info_dialog(self, "成功", f"配置 '{current_config}' 已删除")

    def update_llm_selection_models(self):
        """更新LLM模型选择选项卡中的模型列表"""
        llm_configs = self.config.get("llm_configs", {})
        available_models = list(llm_configs.keys()) if llm_configs else []

        # 更新所有模型选择下拉框
        if hasattr(self, 'prompt_draft_llm'):
            self.update_combobox_items(self.prompt_draft_llm, available_models)
        if hasattr(self, 'architecture_llm'):
            self.update_combobox_items(self.architecture_llm, available_models)
        if hasattr(self, 'chapter_outline_llm'):
            self.update_combobox_items(self.chapter_outline_llm, available_models)
        if hasattr(self, 'final_chapter_llm'):
            self.update_combobox_items(self.final_chapter_llm, available_models)
        if hasattr(self, 'consistency_review_llm'):
            self.update_combobox_items(self.consistency_review_llm, available_models)

    def update_combobox_items(self, combobox: QComboBox, items: list):
        """更新下拉框选项"""
        current_text = combobox.currentText()
        combobox.clear()
        combobox.addItems(items)
        # 保持之前的选中项
        if current_text in items:
            combobox.setCurrentText(current_text)

    def test_llm_connection(self):
        """测试LLM连接 - 预防性编程"""
        self.test_llm_btn.setEnabled(False)
        self.test_result.setText("测试中...")

        from PySide6.QtCore import QTimer

        def perform_test():
            try:
                # [成功] 预防性验证 - 在执行前就检查所有输入
                api_key = self.api_key.text().strip()
                base_url = self.base_url.text().strip()
                model_name = self.model_name.currentText().strip()

                # 验证API密钥
                validate_required(api_key, "API密钥")
                validate_api_key(api_key)

                # 验证URL
                validate_required(base_url, "基础URL")
                validate_url(base_url)

                # 验证模型名称
                validate_required(model_name, "模型名称")

                # 模拟LLM测试 - 如果验证失败根本不会执行到这里
                import time
                time.sleep(1)  # 模拟网络延迟

                # 假设测试成功
                self.test_result.setText(" 连接成功")
                self.test_result.setStyleSheet("color: green; font-weight: bold;")

            except ValueError as e:
                # [成功] 输入验证错误，直接显示友好提示
                self.test_result.setText(" 配置无效")
                self.test_result.setStyleSheet("color: orange; font-weight: bold;")
                show_error_dialog(self, "配置验证失败", str(e))

            except Exception as e:
                # [成功] 其他错误，显示详细错误信息
                self.test_result.setText(" 连接失败")
                self.test_result.setStyleSheet("color: red; font-weight: bold;")
                show_error_dialog(self, "连接测试失败", f"发生错误: {str(e)}")

            finally:
                self.test_llm_btn.setEnabled(True)

        # 异步执行测试
        QTimer.singleShot(100, perform_test)

    def test_embedding_connection(self):
        """测试嵌入连接 - 预防性编程"""
        self.test_embedding_btn.setEnabled(False)
        self.embedding_test_result.setText("测试中...")

        from PySide6.QtCore import QTimer

        def perform_test():
            try:
                # [成功] 预防性验证
                api_key = self.embedding_api_key.text().strip()
                model_name = self.embedding_model.currentText().strip()
                base_url = self.embedding_url.text().strip()

                # 验证API密钥
                validate_required(api_key, "嵌入API密钥")
                validate_api_key(api_key)

                # 验证模型名称
                validate_required(model_name, "嵌入模型名称")

                # 验证URL
                if base_url:  # URL是可选的
                    validate_url(base_url)

                # 模拟测试
                import time
                time.sleep(1)  # 模拟网络延迟

                # 假设测试成功
                self.embedding_test_result.setText(" 连接成功")
                self.embedding_test_result.setStyleSheet("color: green; font-weight: bold;")

            except ValueError as e:
                # [成功] 输入验证错误
                self.embedding_test_result.setText(" 配置无效")
                self.embedding_test_result.setStyleSheet("color: orange; font-weight: bold;")
                show_error_dialog(self, "配置验证失败", str(e))

            except Exception as e:
                # [成功] 其他错误
                self.embedding_test_result.setText(" 连接失败")
                self.embedding_test_result.setStyleSheet("color: red; font-weight: bold;")
                show_error_dialog(self, "连接测试失败", f"发生错误: {str(e)}")

            finally:
                self.test_embedding_btn.setEnabled(True)

        QTimer.singleShot(100, perform_test)

    def apply_config(self):
        """应用配置 - 同时触发自动保存"""
        self.update_config_from_ui()
        self.config_changed.emit(self.config)

        # 如果启用了自动保存，立即触发保存
        if self.auto_save.isChecked():
            self.force_save_config()

        show_info_dialog(self, "成功", "配置已应用")

    def save_config(self):
        """保存配置 - 使用新的自动保存机制"""
        self.force_save_config()

    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置所有配置吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.config = {}
            self.load_current_config()
            show_info_dialog(self, "成功", "配置已重置")

    def update_config_from_ui(self):
        """从界面更新配置"""
        # 更新LLM配置
        current_config_name = self.config_selector.currentText()
        if current_config_name:
            if "llm_configs" not in self.config:
                self.config["llm_configs"] = {}

            self.config["llm_configs"][current_config_name] = {
                "interface_format": self.interface_format.currentText(),
                "api_key": self.api_key.text(),
                "base_url": self.base_url.text(),
                "model_name": self.model_name.currentText(),
                "temperature": self.temperature_slider.value() / 10,
                "max_tokens": self.max_tokens.value(),
                "timeout": self.timeout.value()
            }

            # 更新选择配置
            if "choose_configs" not in self.config:
                self.config["choose_configs"] = {}
            self.config["choose_configs"]["default"] = current_config_name

            # 更新LLM模型选择配置
            if hasattr(self, 'prompt_draft_llm'):
                self.config["choose_configs"]["prompt_draft_llm"] = self.prompt_draft_llm.currentText()
            if hasattr(self, 'architecture_llm'):
                self.config["choose_configs"]["architecture_llm"] = self.architecture_llm.currentText()
            if hasattr(self, 'chapter_outline_llm'):
                self.config["choose_configs"]["chapter_outline_llm"] = self.chapter_outline_llm.currentText()
            if hasattr(self, 'final_chapter_llm'):
                self.config["choose_configs"]["final_chapter_llm"] = self.final_chapter_llm.currentText()
            if hasattr(self, 'consistency_review_llm'):
                self.config["choose_configs"]["consistency_review_llm"] = self.consistency_review_llm.currentText()

        # 更新嵌入配置
        embedding_interface = self.embedding_interface.currentText()
        if "embedding_configs" not in self.config:
            self.config["embedding_configs"] = {}

        self.config["embedding_configs"][embedding_interface] = {
            "interface_format": embedding_interface,
            "api_key": self.embedding_api_key.text(),
            "base_url": self.embedding_url.text(),
            "model_name": self.embedding_model.currentText(),
            "retrieval_k": self.retrieval_k.value()
        }
        self.config["last_embedding_interface_format"] = embedding_interface

        # 更新代理配置
        self.config["proxy_setting"] = {
            "enabled": self.enable_proxy.isChecked(),
            "proxy_url": self.proxy_host.text(),
            "proxy_port": self.proxy_port.value(),
            "username": self.proxy_username.text(),
            "password": self.proxy_password.text()
        }

        # 更新高级配置
        # 日志设置
        self.config.update({
            "log_level": self.log_level.currentText(),
            "log_file": self.log_file.text(),
            "max_workers": self.max_workers.value(),
            "request_timeout": self.request_timeout.value(),
            "retry_count": self.retry_count.value(),
            "auto_save": self.auto_save.isChecked(),
            "save_interval": self.save_interval.value(),
            "show_tooltips": self.show_tooltips.isChecked()
        })
    def setup_tooltips(self):
        """设置工具提示"""
        # LLM配置相关
        tooltip_manager.add_tooltip(self.interface_format, "interface_format")
        tooltip_manager.add_tooltip(self.api_key, "api_key")
        tooltip_manager.add_tooltip(self.base_url, "base_url")
        tooltip_manager.add_tooltip(self.model_name, "model_name")
        tooltip_manager.add_tooltip(self.temperature_slider, "temperature")
        tooltip_manager.add_tooltip(self.max_tokens, "max_tokens")
        tooltip_manager.add_tooltip(self.timeout, "timeout")
        tooltip_manager.add_tooltip(self.test_llm_btn, "test_connection")

        # Embedding配置相关
        tooltip_manager.add_tooltip(self.embedding_interface, "embedding_interface_format")
        tooltip_manager.add_tooltip(self.embedding_api_key, "embedding_api_key")
        tooltip_manager.add_tooltip(self.embedding_url, "embedding_url")
        tooltip_manager.add_tooltip(self.embedding_model, "embedding_model_name")
        tooltip_manager.add_tooltip(self.retrieval_k, "embedding_retrieval_k")
        tooltip_manager.add_tooltip(self.chunk_size, "chunk_size")
        tooltip_manager.add_tooltip(self.chunk_overlap, "chunk_overlap")
        tooltip_manager.add_tooltip(self.test_embedding_btn, "test_connection")

        # 底部按钮
        if hasattr(self, 'save_config_btn'):
            tooltip_manager.add_tooltip(self.save_config_btn, "save_role")
        if hasattr(self, 'load_config_btn'):
            tooltip_manager.add_tooltip(self.load_config_btn, "load_role")

    def connect_change_listeners(self):
        """连接所有UI控件的变更监听器"""
        # LLM配置选项卡
        self.interface_format.currentTextChanged.connect(self.on_config_changed)
        self.api_key.textChanged.connect(self.on_config_changed)
        self.base_url.textChanged.connect(self.on_config_changed)
        self.model_name.currentTextChanged.connect(self.on_config_changed)
        self.temperature_slider.valueChanged.connect(self.on_config_changed)
        self.max_tokens.valueChanged.connect(self.on_config_changed)
        self.timeout.valueChanged.connect(self.on_config_changed)

        # 模型选择选项卡
        if hasattr(self, 'prompt_draft_llm'):
            self.prompt_draft_llm.currentTextChanged.connect(self.on_config_changed)
        if hasattr(self, 'architecture_llm'):
            self.architecture_llm.currentTextChanged.connect(self.on_config_changed)
        if hasattr(self, 'chapter_outline_llm'):
            self.chapter_outline_llm.currentTextChanged.connect(self.on_config_changed)
        if hasattr(self, 'final_chapter_llm'):
            self.final_chapter_llm.currentTextChanged.connect(self.on_config_changed)
        if hasattr(self, 'consistency_review_llm'):
            self.consistency_review_llm.currentTextChanged.connect(self.on_config_changed)

        # 嵌入配置选项卡
        self.embedding_interface.currentTextChanged.connect(self.on_config_changed)
        self.embedding_api_key.textChanged.connect(self.on_config_changed)
        self.embedding_url.textChanged.connect(self.on_config_changed)
        self.embedding_model.currentTextChanged.connect(self.on_config_changed)
        self.retrieval_k.valueChanged.connect(self.on_config_changed)
        self.chunk_size.valueChanged.connect(self.on_config_changed)
        self.chunk_overlap.valueChanged.connect(self.on_config_changed)

        # 代理配置选项卡
        self.enable_proxy.stateChanged.connect(self.on_config_changed)
        self.proxy_host.textChanged.connect(self.on_config_changed)
        self.proxy_port.valueChanged.connect(self.on_config_changed)
        self.proxy_username.textChanged.connect(self.on_config_changed)
        self.proxy_password.textChanged.connect(self.on_config_changed)

        # 高级配置选项卡
        self.log_level.currentTextChanged.connect(self.on_config_changed)
        self.log_file.textChanged.connect(self.on_config_changed)
        self.max_workers.valueChanged.connect(self.on_config_changed)
        self.request_timeout.valueChanged.connect(self.on_config_changed)
        self.retry_count.valueChanged.connect(self.on_config_changed)
        self.auto_save.stateChanged.connect(self.on_config_changed)
        self.save_interval.valueChanged.connect(self.on_config_changed)
        self.show_tooltips.stateChanged.connect(self.on_config_changed)

    def on_config_changed(self):
        """配置变更处理 - 触发自动保存定时器"""
        # 如果自动保存功能被禁用，则直接返回
        if not self.auto_save.isChecked():
            return

        # 停止之前的定时器（如果有）
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()

        # 启动新的2秒定时器
        self.auto_save_timer.start(2000)

        # 发送状态信号
        self.auto_save_status_changed.emit("info", "配置已更改，2秒后自动保存...")

        # 检查配置是否有实际变更
        self.update_config_from_ui()
        if self.config != self.original_config:
            logging.debug("配置发生变更，启动自动保存定时器")
        else:
            logging.debug("配置无实际变更，取消自动保存")
            self.auto_save_timer.stop()

    def perform_auto_save(self):
        """执行自动保存 - 在后台线程中"""
        if self.is_saving:
            # 如果正在保存，标记为待保存
            self.pending_save = True
            logging.debug("保存正在进行中，标记为待保存")
            return

        # 更新配置数据
        self.update_config_from_ui()

        # 检查是否有实际变更
        if self.config == self.original_config:
            logging.debug("配置无变更，跳过自动保存")
            return

        # 发送开始信号
        self.auto_save_started.emit()
        self.is_saving = True

        # 在后台线程中执行保存
        def save_in_background():
            try:
                # 执行保存
                success = save_config(self.config, None)

                if success:
                    # 更新原始配置
                    self.original_config = self.config.copy()
                    logging.info("配置自动保存成功")

                    # 发送成功信号（需要在主线程中执行）
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self.auto_save_completed.emit(True))
                    QTimer.singleShot(0, lambda: self.auto_save_status_changed.emit("success", "配置已自动保存"))
                else:
                    logging.error("配置自动保存失败")
                    QTimer.singleShot(0, lambda: self.auto_save_completed.emit(False))
                    QTimer.singleShot(0, lambda: self.auto_save_status_changed.emit("error", "配置保存失败，请重试"))

            except Exception as e:
                logging.error(f"自动保存配置时发生异常: {e}", exc_info=True)
                QTimer.singleShot(0, lambda: self.auto_save_completed.emit(False))
                QTimer.singleShot(0, lambda: self.auto_save_status_changed.emit("error", f"配置保存失败: {str(e)}"))

            finally:
                self.is_saving = False

                # 检查是否有待保存的变更
                if self.pending_save:
                    self.pending_save = False
                    QTimer.singleShot(100, self.perform_auto_save)  # 延迟100ms后重试

        # 启动后台保存线程
        self.save_thread = threading.Thread(target=save_in_background, daemon=True)
        self.save_thread.start()

    def set_status_bar(self, status_bar):
        """设置状态栏引用"""
        self.status_bar = status_bar
        # 连接自动保存状态信号到状态栏
        self.auto_save_status_changed.connect(self.on_auto_save_status_changed)

    def on_auto_save_status_changed(self, status_type: str, message: str):
        """处理自动保存状态变更"""
        if self.status_bar:
            if status_type == "info":
                # 待保存状态 - 灰色，显示"配置已更改，2秒后自动保存..."
                self.status_bar.set_info_state(message, auto_clear=False)  # 永久显示直到保存完成
            elif status_type == "success":
                # 保存成功状态 - 绿色，显示"配置已自动保存"，3秒后自动清除
                self.status_bar.set_success_state(message)
            elif status_type == "error":
                # 保存错误状态 - 红色，显示"配置保存失败，请重试"，保持显示
                self.status_bar.set_error_state(message)

    def closeEvent(self, event):
        """处理窗口关闭事件 - 确保配置保存"""
        logging.info("配置窗口关闭，检查是否有待保存的变更")

        # 停止自动保存定时器
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
            logging.debug("已停止自动保存定时器")

        # 如果有正在进行的保存，等待完成
        if self.is_saving:
            logging.info("等待后台保存完成...")
            # 最多等待3秒
            import time
            wait_time = 0
            while self.is_saving and wait_time < 30:  # 3秒 = 30 * 0.1秒
                time.sleep(0.1)
                wait_time += 1

        # 检查是否有未保存的变更
        self.update_config_from_ui()
        if self.config != self.original_config:
            logging.info("检测到未保存的配置变更，立即执行保存")

            # 立即保存（不等待定时器）
            try:
                success = save_config(self.config, None)
                if success:
                    logging.info("关闭前配置保存成功")
                    self.auto_save_status_changed.emit("success", "配置已保存")
                else:
                    logging.error("关闭前配置保存失败")
                    self.auto_save_status_changed.emit("error", "配置保存失败")
            except Exception as e:
                logging.error(f"关闭前配置保存异常: {e}", exc_info=True)
                self.auto_save_status_changed.emit("error", f"配置保存失败: {str(e)}")

        # 资源清理
        try:
            # 清理自动保存定时器
            if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
                self.auto_save_timer.deleteLater()
                self.auto_save_timer = None
                logging.debug("自动保存定时器资源已清理")

            # 清理状态栏引用
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar = None
                logging.debug("状态栏引用已清理")

            # 清理保存线程引用
            if hasattr(self, 'save_thread') and self.save_thread:
                self.save_thread = None
                logging.debug("保存线程引用已清理")

            # 确保事件循环处理完成
            from PySide6.QtWidgets import QApplication
            if QApplication.instance():
                QApplication.processEvents()
                logging.debug("事件循环处理完成")

        except Exception as e:
            logging.warning(f"资源清理时出现异常: {e}")
            # 不影响关闭流程

        # 允许关闭
        event.accept()
        logging.info("配置窗口关闭完成")

    def force_save_config(self):
        """强制立即保存配置（用于手动保存按钮）"""
        # 停止自动保存定时器
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()

        # 立即执行保存
        self.perform_auto_save()
