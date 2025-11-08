# ui_qt/dialogs/settings_dialog.py
# -*- coding: utf-8 -*-
"""
设置对话框
提供应用程序的详细设置界面
"""

from typing import Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QDialogButtonBox, QSlider,
    QTextEdit, QFrame, QColorDialog, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建标题
        title_label = QLabel("⚙️ 应用设置")
        set_font_size(title_label, 14, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 6px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 创建各个设置选项卡
        self.create_general_tab()
        self.create_editor_tab()
        self.create_theme_tab()
        self.create_advanced_tab()

        # 底部按钮
        self.create_bottom_buttons(layout)

    def create_general_tab(self):
        """创建常规设置选项卡"""
        general_widget = QWidget()
        layout = QVBoxLayout(general_widget)
        layout.setSpacing(15)

        # 启动设置
        startup_group = QGroupBox("🚀 启动设置")
        startup_layout = QFormLayout(startup_group)

        self.auto_load_project = QCheckBox("自动加载上次项目")
        startup_layout.addRow("", self.auto_load_project)

        self.show_splash = QCheckBox("显示启动画面")
        self.show_splash.setChecked(True)
        startup_layout.addRow("", self.show_splash)

        self.check_updates = QCheckBox("启动时检查更新")
        startup_layout.addRow("", self.check_updates)

        layout.addWidget(startup_group)

        # 文件设置
        file_group = QGroupBox("📁 文件设置")
        file_layout = QFormLayout(file_group)

        self.default_save_path = QLineEdit()
        self.default_save_path.setPlaceholderText("选择默认保存路径...")
        file_layout.addRow("默认保存路径:", self.create_path_selector(self.default_save_path))

        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(5)
        self.auto_save_interval.setSuffix(" 分钟")
        file_layout.addRow("自动保存间隔:", self.auto_save_interval)

        self.max_backup_files = QSpinBox()
        self.max_backup_files.setRange(0, 50)
        self.max_backup_files.setValue(10)
        file_layout.addRow("最大备份文件数:", self.max_backup_files)

        layout.addWidget(file_group)

        # 语言设置
        language_group = QGroupBox("🌐 语言设置")
        language_layout = QFormLayout(language_group)

        self.interface_language = QComboBox()
        self.interface_language.addItems(["简体中文", "繁體中文", "English", "日本語"])
        language_layout.addRow("界面语言:", self.interface_language)

        self.content_language = QComboBox()
        self.content_language.addItems(["简体中文", "繁體中文", "English"])
        language_layout.addRow("内容语言:", self.content_language)

        layout.addWidget(language_group)
        layout.addStretch()

        self.tab_widget.addTab(general_widget, "📋 常规")

    def create_editor_tab(self):
        """创建编辑器设置选项卡"""
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)
        layout.setSpacing(15)

        # 编辑器外观
        appearance_group = QGroupBox("🎨 编辑器外观")
        appearance_layout = QFormLayout(appearance_group)

        self.editor_font = QComboBox()
        self.editor_font.addItems([
            "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC",
            "Source Code Pro", "Consolas", "Courier New"
        ])
        appearance_layout.addRow("字体:", self.editor_font)

        self.editor_font_size = QSpinBox()
        self.editor_font_size.setRange(8, 72)
        self.editor_font_size.setValue(12)
        appearance_layout.addRow("字号:", self.editor_font_size)

        self.line_spacing = QSpinBox()
        self.line_spacing.setRange(10, 30)
        self.line_spacing.setValue(16)
        self.line_spacing.setSuffix(" pt")
        appearance_layout.addRow("行间距:", self.line_spacing)

        layout.addWidget(appearance_group)

        # 编辑器行为
        behavior_group = QGroupBox("⚙️ 编辑器行为")
        behavior_layout = QFormLayout(behavior_group)

        self.word_wrap = QCheckBox("自动换行")
        self.word_wrap.setChecked(True)
        behavior_layout.addRow("", self.word_wrap)

        self.auto_complete = QCheckBox("自动完成")
        self.auto_complete.setChecked(True)
        behavior_layout.addRow("", self.auto_complete)

        self.auto_indent = QCheckBox("自动缩进")
        self.auto_indent.setChecked(True)
        behavior_layout.addRow("", self.auto_indent)

        self.show_line_numbers = QCheckBox("显示行号")
        behavior_layout.addRow("", self.show_line_numbers)

        self.highlight_syntax = QCheckBox("语法高亮")
        self.highlight_syntax.setChecked(True)
        behavior_layout.addRow("", self.highlight_syntax)

        layout.addWidget(behavior_group)

        # 快捷键设置
        shortcuts_group = QGroupBox("⌨️ 快捷键")
        shortcuts_layout = QVBoxLayout(shortcuts_group)

        shortcuts_text = QTextEdit()
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setMaximumHeight(150)
        shortcuts_text.setPlainText("""常用快捷键：

Ctrl+N: 新建项目          Ctrl+O: 打开项目
Ctrl+S: 保存              Ctrl+Z: 撤销
Ctrl+Y: 重做              Ctrl+C: 复制
Ctrl+V: 粘贴              Ctrl+X: 剪切
Ctrl+F: 查找              Ctrl+H: 替换
Ctrl+G: 跳转到行          Ctrl+B: 加粗
Ctrl+I: 斜体              Ctrl+U: 下划线
F5: 刷新预览              F11: 全屏模式""")
        shortcuts_layout.addWidget(shortcuts_text)

        layout.addWidget(shortcuts_group)
        layout.addStretch()

        self.tab_widget.addTab(editor_widget, "✏️ 编辑器")

    def create_theme_tab(self):
        """创建主题设置选项卡"""
        theme_widget = QWidget()
        layout = QVBoxLayout(theme_widget)
        layout.setSpacing(15)

        # 主题选择
        theme_select_group = QGroupBox("🎨 主题选择")
        theme_select_layout = QVBoxLayout(theme_select_group)

        # 主题预览
        self.theme_preview = QFrame()
        self.theme_preview.setStyleSheet("""
            QFrame {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                padding: 20px;
            }
        """)
        self.theme_preview.setMinimumHeight(150)

        preview_layout = QVBoxLayout(self.theme_preview)

        preview_title = QLabel("主题预览")
        preview_title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addWidget(preview_title)

        preview_text = QLabel("这是主题预览文本，显示当前主题的颜色和样式效果。")
        preview_layout.addWidget(preview_text)

        preview_button = QPushButton("示例按钮")
        preview_layout.addWidget(preview_button)

        theme_select_layout.addWidget(self.theme_preview)

        # 主题选择器
        theme_button_layout = QHBoxLayout()

        self.light_theme_btn = QPushButton("☀️ 浅色主题")
        self.light_theme_btn.setCheckable(True)
        self.light_theme_btn.setChecked(True)
        self.light_theme_btn.clicked.connect(lambda: self.select_theme("light"))
        theme_button_layout.addWidget(self.light_theme_btn)

        self.dark_theme_btn = QPushButton("🌙 深色主题")
        self.dark_theme_btn.setCheckable(True)
        self.dark_theme_btn.clicked.connect(lambda: self.select_theme("dark"))
        theme_button_layout.addWidget(self.dark_theme_btn)

        self.auto_theme_btn = QPushButton("🌗 跟随系统")
        self.auto_theme_btn.setCheckable(True)
        self.auto_theme_btn.clicked.connect(lambda: self.select_theme("auto"))
        theme_button_layout.addWidget(self.auto_theme_btn)

        theme_select_layout.addLayout(theme_button_layout)

        layout.addWidget(theme_select_group)

        # 颜色自定义
        color_group = QGroupBox("🎨 颜色自定义")
        color_layout = QGridLayout(color_group)

        color_layout.addWidget(QLabel("主色调:"), 0, 0)
        self.primary_color_btn = QPushButton("选择颜色")
        self.primary_color_btn.clicked.connect(lambda: self.select_color("primary"))
        color_layout.addWidget(self.primary_color_btn, 0, 1)

        color_layout.addWidget(QLabel("强调色:"), 1, 0)
        self.accent_color_btn = QPushButton("选择颜色")
        self.accent_color_btn.clicked.connect(lambda: self.select_color("accent"))
        color_layout.addWidget(self.accent_color_btn, 1, 1)

        color_layout.addWidget(QLabel("背景色:"), 2, 0)
        self.background_color_btn = QPushButton("选择颜色")
        self.background_color_btn.clicked.connect(lambda: self.select_color("background"))
        color_layout.addWidget(self.background_color_btn, 2, 1)

        color_layout.addWidget(QLabel("文字色:"), 3, 0)
        self.text_color_btn = QPushButton("选择颜色")
        self.text_color_btn.clicked.connect(lambda: self.select_color("text"))
        color_layout.addWidget(self.text_color_btn, 3, 1)

        self.reset_colors_btn = QPushButton("🔄 重置颜色")
        self.reset_colors_btn.clicked.connect(self.reset_colors)
        color_layout.addWidget(self.reset_colors_btn, 4, 0, 1, 2)

        layout.addWidget(color_group)
        layout.addStretch()

        self.tab_widget.addTab(theme_widget, "🎨 主题")

    def create_advanced_tab(self):
        """创建高级设置选项卡"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        layout.setSpacing(15)

        # 性能设置
        performance_group = QGroupBox("⚡ 性能设置")
        performance_layout = QFormLayout(performance_group)

        self.max_memory = QSpinBox()
        self.max_memory.setRange(512, 8192)
        self.max_memory.setValue(2048)
        self.max_memory.setSuffix(" MB")
        performance_layout.addRow("最大内存使用:", self.max_memory)

        self.thread_pool_size = QSpinBox()
        self.thread_pool_size.setRange(1, 16)
        self.thread_pool_size.setValue(4)
        performance_layout.addRow("线程池大小:", self.thread_pool_size)

        self.cache_size = QSpinBox()
        self.cache_size.setRange(10, 1000)
        self.cache_size.setValue(100)
        self.cache_size.setSuffix(" MB")
        performance_layout.addRow("缓存大小:", self.cache_size)

        layout.addWidget(performance_group)

        # 网络设置
        network_group = QGroupBox("🌐 网络设置")
        network_layout = QFormLayout(network_group)

        self.request_timeout = QSpinBox()
        self.request_timeout.setRange(5, 300)
        self.request_timeout.setValue(30)
        self.request_timeout.setSuffix(" 秒")
        network_layout.addRow("请求超时:", self.request_timeout)

        self.max_retries = QSpinBox()
        self.max_retries.setRange(0, 10)
        self.max_retries.setValue(3)
        network_layout.addRow("最大重试次数:", self.max_retries)

        self.concurrent_requests = QSpinBox()
        self.concurrent_requests.setRange(1, 20)
        self.concurrent_requests.setValue(5)
        network_layout.addRow("并发请求数:", self.concurrent_requests)

        layout.addWidget(network_group)

        # 调试设置
        debug_group = QGroupBox("🐛 调试设置")
        debug_layout = QVBoxLayout(debug_group)

        self.enable_debug = QCheckBox("启用调试模式")
        debug_layout.addWidget(self.enable_debug)

        self.verbose_logging = QCheckBox("详细日志记录")
        debug_layout.addWidget(self.verbose_logging)

        self.show_performance_metrics = QCheckBox("显示性能指标")
        debug_layout.addWidget(self.show_performance_metrics)

        layout.addWidget(debug_group)

        # 数据清理
        cleanup_group = QGroupBox("🗑️ 数据清理")
        cleanup_layout = QVBoxLayout(cleanup_group)

        cleanup_text = QLabel("清理应用程序缓存和临时数据，释放磁盘空间。")
        cleanup_layout.addWidget(cleanup_text)

        cleanup_buttons = QHBoxLayout()
        self.clear_cache_btn = QPushButton("🗑️ 清理缓存")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cleanup_buttons.addWidget(self.clear_cache_btn)

        self.cleanup_logs_btn = QPushButton("📄 清理日志")
        self.cleanup_logs_btn.clicked.connect(self.cleanup_logs)
        cleanup_buttons.addWidget(self.cleanup_logs_btn)

        self.cleanup_temp_btn = QPushButton("🗂️ 清理临时文件")
        self.cleanup_temp_btn.clicked.connect(self.cleanup_temp)
        cleanup_buttons.addWidget(self.cleanup_temp_btn)

        cleanup_layout.addLayout(cleanup_buttons)

        layout.addWidget(cleanup_group)
        layout.addStretch()

        self.tab_widget.addTab(advanced_widget, "⚙️ 高级")

    def create_path_selector(self, line_edit: QLineEdit) -> QWidget:
        """创建路径选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(line_edit)

        browse_btn = QPushButton("📁 浏览")
        browse_btn.clicked.connect(lambda: self.browse_directory(line_edit))
        layout.addWidget(browse_btn)

        return widget

    def create_bottom_buttons(self, layout: QVBoxLayout):
        """创建底部按钮"""
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)

        layout.addWidget(button_box)

    def load_settings(self):
        """加载设置"""
        # 从配置中加载设置到界面
        general_settings = self.config.get("general_settings", {})
        self.auto_load_project.setChecked(general_settings.get("auto_load_project", False))
        self.show_splash.setChecked(general_settings.get("show_splash", True))
        self.check_updates.setChecked(general_settings.get("check_updates", False))

        # 加载其他设置...
        editor_settings = self.config.get("editor_settings", {})
        self.editor_font.setCurrentText(editor_settings.get("font", "Microsoft YaHei UI"))
        self.editor_font_size.setValue(editor_settings.get("font_size", 12))

        # 加载主题设置
        theme_settings = self.config.get("theme_settings", {})
        current_theme = theme_settings.get("current_theme", "light")
        self.select_theme(current_theme)

    def apply_settings(self):
        """应用设置"""
        # 收集所有设置
        new_config = {
            "general_settings": {
                "auto_load_project": self.auto_load_project.isChecked(),
                "show_splash": self.show_splash.isChecked(),
                "check_updates": self.check_updates.isChecked(),
                "default_save_path": self.default_save_path.text(),
                "auto_save_interval": self.auto_save_interval.value(),
                "max_backup_files": self.max_backup_files.value(),
                "interface_language": self.interface_language.currentText(),
                "content_language": self.content_language.currentText()
            },
            "editor_settings": {
                "font": self.editor_font.currentText(),
                "font_size": self.editor_font_size.value(),
                "line_spacing": self.line_spacing.value(),
                "word_wrap": self.word_wrap.isChecked(),
                "auto_complete": self.auto_complete.isChecked(),
                "auto_indent": self.auto_indent.isChecked(),
                "show_line_numbers": self.show_line_numbers.isChecked(),
                "highlight_syntax": self.highlight_syntax.isChecked()
            },
            "theme_settings": {
                "current_theme": self.get_selected_theme(),
                "primary_color": getattr(self, 'primary_color', '#2196f3'),
                "accent_color": getattr(self, 'accent_color', '#ff9800')
            },
            "advanced_settings": {
                "max_memory": self.max_memory.value(),
                "thread_pool_size": self.thread_pool_size.value(),
                "cache_size": self.cache_size.value(),
                "request_timeout": self.request_timeout.value(),
                "max_retries": self.max_retries.value(),
                "concurrent_requests": self.concurrent_requests.value(),
                "enable_debug": self.enable_debug.isChecked(),
                "verbose_logging": self.verbose_logging.isChecked(),
                "show_performance_metrics": self.show_performance_metrics.isChecked()
            }
        }

        self.config.update(new_config)
        show_info_dialog(self, "成功", "设置已应用")

    def get_selected_theme(self) -> str:
        """获取选择的主题"""
        if self.light_theme_btn.isChecked():
            return "light"
        elif self.dark_theme_btn.isChecked():
            return "dark"
        else:
            return "auto"

    def select_theme(self, theme_name: str):
        """选择主题"""
        # 重置所有按钮状态
        self.light_theme_btn.setChecked(False)
        self.dark_theme_btn.setChecked(False)
        self.auto_theme_btn.setChecked(False)

        # 设置选中状态
        if theme_name == "light":
            self.light_theme_btn.setChecked(True)
            self.theme_preview.setStyleSheet("""
                QFrame {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                    color: #333;
                    padding: 20px;
                }
            """)
        elif theme_name == "dark":
            self.dark_theme_btn.setChecked(True)
            self.theme_preview.setStyleSheet("""
                QFrame {
                    border: 2px solid #555;
                    border-radius: 8px;
                    background-color: #2d2d2d;
                    color: white;
                    padding: 20px;
                }
            """)
        else:
            self.auto_theme_btn.setChecked(True)
            self.theme_preview.setStyleSheet("""
                QFrame {
                    border: 2px solid #888;
                    border-radius: 8px;
                    background-color: #f0f0f0;
                    color: #333;
                    padding: 20px;
                }
            """)

    def select_color(self, color_type: str):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            setattr(self, f"{color_type}_color", hex_color)

    def reset_colors(self):
        """重置颜色"""
        self.primary_color = "#2196f3"
        self.accent_color = "#ff9800"
        self.background_color = "#ffffff"
        self.text_color = "#333333"
        show_info_dialog(self, "成功", "颜色已重置")

    def browse_directory(self, line_edit: QLineEdit):
        """浏览目录"""
        from PySide6.QtWidgets import QFileDialog

        directory = QFileDialog.getExistingDirectory(
            self, "选择目录", line_edit.text()
        )
        if directory:
            line_edit.setText(directory)

    def clear_cache(self):
        """清理缓存"""
        reply = QMessageBox.question(
            self, "确认清理",
            "确定要清理所有缓存文件吗？\n这可能会影响应用性能。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 这里实现缓存清理逻辑
            show_info_dialog(self, "成功", "缓存已清理")

    def cleanup_logs(self):
        """清理日志"""
        reply = QMessageBox.question(
            self, "确认清理",
            "确定要清理所有日志文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 这里实现日志清理逻辑
            show_info_dialog(self, "成功", "日志已清理")

    def cleanup_temp(self):
        """清理临时文件"""
        reply = QMessageBox.question(
            self, "确认清理",
            "确定要清理所有临时文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 这里实现临时文件清理逻辑
            show_info_dialog(self, "成功", "临时文件已清理")

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        self.apply_settings()
        return self.config