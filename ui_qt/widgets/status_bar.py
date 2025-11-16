# ui_qt/widgets/status_bar.py
# -*- coding: utf-8 -*-
"""
状态栏组件
显示应用程序状态信息和进度
"""

from typing import Optional
from PySide6.QtWidgets import (
    QStatusBar, QLabel, QWidget, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QFont


class StatusBar(QStatusBar):
    """自定义状态栏组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.message_timer = QTimer()
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.clear_message)

    def setup_ui(self):
        """设置状态栏UI"""
        # 创建主状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setMinimumWidth(200)
        self.addWidget(self.status_label)

        # 添加分隔符
        separator1 = QLabel("|")
        separator1.setObjectName("StatusBarSeparator")
        self.addWidget(separator1)

        # 创建进度条（默认隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        self.addWidget(self.progress_bar)

        # 添加分隔符
        separator2 = QLabel("|")
        separator2.setObjectName("StatusBarSeparator")
        self.addWidget(separator2)

        # 创建生成状态指示器
        self.generation_status = QLabel("空闲")
        self.generation_status.setObjectName("GenerationStatusIndicator")
        self.generation_status.setStyleSheet("""
            QLabel {
                padding: 2px 8px;
                border-radius: 3px;
                background-color: #e8f5e8;
                color: #2e7d2e;
            }
        """)
        self.addWidget(self.generation_status)

        # 添加分隔符
        separator3 = QLabel("|")
        separator3.setObjectName("StatusBarSeparator")
        self.addWidget(separator3)

        # 创建项目路径标签
        self.project_label = QLabel("未打开项目")
        self.project_label.setMinimumWidth(200)
        self.addWidget(self.project_label)

        # 创建永久状态信息（右侧）
        self.permanent_widget = QWidget()
        permanent_layout = QHBoxLayout(self.permanent_widget)
        permanent_layout.setContentsMargins(0, 0, 0, 0)
        permanent_layout.setSpacing(10)

        # 主题状态
        self.theme_label = QLabel("浅色主题")
        permanent_layout.addWidget(self.theme_label)

        # 添加分隔符
        separator4 = QLabel("|")
        separator4.setObjectName("StatusBarSeparator")
        permanent_layout.addWidget(separator4)

        # 时间显示
        self.time_label = QLabel()
        permanent_layout.addWidget(self.time_label)

        self.addPermanentWidget(self.permanent_widget)

        # 设置定时器更新时间
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # 每秒更新一次
        self.update_time()

    def show_message(self, message: str, timeout: int = 0):
        """显示状态消息

        Args:
            message: 消息内容
            timeout: 显示时间(毫秒)，0表示永久显示
        """
        self.status_label.setText(message)
        if timeout > 0:
            self.message_timer.start(timeout)

    def clear_message(self):
        """清除状态消息"""
        self.status_label.setText("就绪")

    def set_generating(self, is_generating: bool):
        """设置生成状态

        Args:
            is_generating: 是否正在生成
        """
        if is_generating:
            self.generation_status.setText("生成中...")
            # 使用CSS类来支持主题感知
            self.generation_status.setProperty("status", "generating")
            self.generation_status.style().unpolish(self.generation_status)
            self.generation_status.style().polish(self.generation_status)
        else:
            self.generation_status.setText("空闲")
            # 使用CSS类来支持主题感知
            self.generation_status.setProperty("status", "idle")
            self.generation_status.style().unpolish(self.generation_status)
            self.generation_status.style().polish(self.generation_status)

    def set_progress(self, value: int, maximum: int = 100, text: str = ""):
        """设置进度条

        Args:
            value: 当前进度值
            maximum: 最大值
            text: 进度文本
        """
        if maximum > 0:
            self.progress_bar.setMaximum(maximum)
            self.progress_bar.setValue(value)
            if text:
                self.progress_bar.setFormat(text)
            self.progress_bar.show()
        else:
            self.progress_bar.hide()

    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.hide()

    def set_project_path(self, path: str):
        """设置项目路径

        Args:
            path: 项目路径
        """
        if path:
            # 截断过长的路径
            if len(path) > 30:
                path = "..." + path[-27:]
            self.project_label.setText(f"项目: {path}")
        else:
            self.project_label.setText("未打开项目")

    def set_theme(self, theme_name: str):
        """设置主题状态

        Args:
            theme_name: 主题名称
        """
        self.theme_label.setText(f"{theme_name}主题")

    def update_theme_display(self, theme_name: str):
        """更新主题显示（用于深浅色切换）

        Args:
            theme_name: 主题名称 ('light' 或 'dark')
        """
        # 更新主题标签文本
        if theme_name == "dark":
            self.theme_label.setText("深色主题")
        else:
            self.theme_label.setText("浅色主题")

    def update_time(self):
        """更新时间显示"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def set_error_state(self, message: str):
        """设置错误状态

        Args:
            message: 错误消息
        """
        self.status_label.setText(f"错误: {message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-weight: bold;
            }
        """)

        # 3秒后恢复正常样式
        QTimer.singleShot(3000, self.clear_error_state)

    def clear_error_state(self):
        """清除错误状态"""
        self.status_label.setStyleSheet("")
        self.clear_message()

    def set_warning_state(self, message: str):
        """设置警告状态

        Args:
            message: 警告消息
        """
        self.status_label.setText(f"警告: {message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f57c00;
                font-weight: bold;
            }
        """)

        # 3秒后恢复正常样式
        QTimer.singleShot(3000, self.clear_warning_state)

    def clear_warning_state(self):
        """清除警告状态"""
        self.status_label.setStyleSheet("")
        self.clear_message()

    def set_success_state(self, message: str, auto_clear: bool = True):
        """设置成功状态

        Args:
            message: 成功消息
            auto_clear: 是否自动清除（默认True，3秒后清除）
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #388e3c;
                font-weight: bold;
            }
        """)

        # 3秒后恢复正常样式（如果启用了自动清除）
        if auto_clear:
            QTimer.singleShot(3000, self.clear_success_state)

    def clear_success_state(self):
        """清除成功状态"""
        self.status_label.setStyleSheet("")
        self.clear_message()

    def set_info_state(self, message: str, auto_clear: bool = False):
        """设置信息状态（用于自动保存待处理状态）

        Args:
            message: 信息消息
            auto_clear: 是否自动清除（默认False，永久显示）
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-weight: normal;
            }
        """)

        # 如果启用了自动清除，指定时间后恢复正常样式
        if auto_clear:
            QTimer.singleShot(auto_clear if isinstance(auto_clear, int) else 3000, self.clear_info_state)

    def clear_info_state(self):
        """清除信息状态"""
        self.status_label.setStyleSheet("")
        self.clear_message()

    def add_custom_widget(self, widget, permanent: bool = False):
        """添加自定义控件到状态栏

        Args:
            widget: 控件实例
            permanent: 是否永久显示
        """
        if permanent:
            self.addPermanentWidget(widget)
        else:
            self.addWidget(widget)

    def remove_custom_widget(self, widget):
        """从状态栏移除自定义控件

        Args:
            widget: 控件实例
        """
        self.removeWidget(widget)
        widget.deleteLater()