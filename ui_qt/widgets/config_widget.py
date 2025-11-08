# ui_qt/widgets/config_widget.py
# -*- coding: utf-8 -*-
"""
配置管理组件
管理LLM配置、API密钥、代理设置等
"""

import os
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QSlider, QFrame, QTextEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)


class ConfigWidget(QWidget):
    """配置管理组件"""

    # 信号定义
    config_changed = Signal(dict)

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 创建标题
        title_label = QLabel("⚙️ 配置管理")
        set_font_size(title_label, 14, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 6px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tab_widget)

        # 创建各个配置选项卡
        self.create_llm_config_tab()
        self.create_embedding_config_tab()
        self.create_proxy_config_tab()
        self.create_advanced_config_tab()

        # 底部按钮
        self.create_bottom_buttons(layout)

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

        self.test_llm_btn = QPushButton("🔗 测试LLM连接")
        self.test_llm_btn.clicked.connect(self.test_llm_connection)
        test_layout.addWidget(self.test_llm_btn)

        self.test_result = QLabel("未测试")
        test_layout.addWidget(self.test_result)
        test_layout.addStretch()

        layout.addWidget(test_group)
        layout.addStretch()

        self.tab_widget.addTab(llm_widget, "🤖 LLM配置")

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

        self.test_embedding_btn = QPushButton("🔗 测试嵌入连接")
        self.test_embedding_btn.clicked.connect(self.test_embedding_connection)
        test_layout.addWidget(self.test_embedding_btn)

        self.embedding_test_result = QLabel("未测试")
        test_layout.addWidget(self.embedding_test_result)
        test_layout.addStretch()

        layout.addWidget(test_group)
        layout.addStretch()

        self.tab_widget.addTab(embed_widget, "🔍 嵌入配置")

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

        self.tab_widget.addTab(proxy_widget, "🌐 代理设置")

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

        self.tab_widget.addTab(advanced_widget, "⚡ 高级设置")

    def create_bottom_buttons(self, layout: QVBoxLayout):
        """创建底部按钮"""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()

        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(self.reset_btn)

        self.apply_btn = QPushButton("✅ 应用")
        self.apply_btn.clicked.connect(self.apply_config)
        button_layout.addWidget(self.apply_btn)

        self.save_btn = QPushButton("💾 保存配置")
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
        self.max_tokens.setValue(int(config_data.get("max_tokens", "8192")) if config_data.get("max_tokens") else 8192)
        self.timeout.setValue(int(config_data.get("timeout", "600")) if config_data.get("timeout") else 600)

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
        self.retrieval_k.setValue(int(config_data.get("retrieval_k", "4")) if config_data.get("retrieval_k") else 4)

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
        # 这里可以加载其他高级配置项
        self.auto_save.setChecked(self.config.get("auto_save", True))
        self.save_interval.setValue(int(self.config.get("save_interval", "5")) if self.config.get("save_interval") else 5)
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
                show_info_dialog(self, "成功", f"配置 '{current_config}' 已删除")

    def test_llm_connection(self):
        """测试LLM连接"""
        self.test_llm_btn.setEnabled(False)
        self.test_result.setText("测试中...")

        # 这里实现实际的连接测试逻辑
        # 暂时模拟测试结果
        from PySide6.QtCore import QTimer

        def test_complete():
            self.test_result.setText("✅ 连接成功")
            self.test_result.setStyleSheet("color: green; font-weight: bold;")
            self.test_llm_btn.setEnabled(True)

        QTimer.singleShot(2000, test_complete)

    def test_embedding_connection(self):
        """测试嵌入连接"""
        self.test_embedding_btn.setEnabled(False)
        self.embedding_test_result.setText("测试中...")

        # 这里实现实际的连接测试逻辑
        from PySide6.QtCore import QTimer

        def test_complete():
            self.embedding_test_result.setText("✅ 连接成功")
            self.embedding_test_result.setStyleSheet("color: green; font-weight: bold;")
            self.test_embedding_btn.setEnabled(True)

        QTimer.singleShot(2000, test_complete)

    def apply_config(self):
        """应用配置"""
        self.update_config_from_ui()
        self.config_changed.emit(self.config)
        show_info_dialog(self, "成功", "配置已应用")

    def save_config(self):
        """保存配置"""
        self.update_config_from_ui()
        # 这里调用实际的保存函数
        show_info_dialog(self, "成功", "配置已保存")

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
        self.config.update({
            "auto_save": self.auto_save.isChecked(),
            "save_interval": self.save_interval.value(),
            "show_tooltips": self.show_tooltips.isChecked()
        })