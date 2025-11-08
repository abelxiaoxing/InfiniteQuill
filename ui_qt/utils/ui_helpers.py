# ui_qt/utils/ui_helpers.py
# -*- coding: utf-8 -*-
"""
UI辅助函数
提供常用的界面组件创建和操作函数
"""

import re
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout,
    QMessageBox, QProgressDialog, QSizePolicy, QSpacerItem,
    QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


def create_separator(orientation: str = "horizontal", width: int = 1) -> QFrame:
    """创建分隔线

    Args:
        orientation: 方向 ("horizontal" 或 "vertical")
        width: 线宽

    Returns:
        QFrame: 分隔线控件
    """
    separator = QFrame()
    if orientation == "horizontal":
        separator.setFrameShape(QFrame.HLine)
        separator.setMaximumHeight(width)
    else:
        separator.setFrameShape(QFrame.VLine)
        separator.setMaximumWidth(width)

    separator.setFrameShadow(QFrame.Sunken)
    separator.setStyleSheet("background-color: #c0c0c0;")

    return separator


def create_spacer(horizontal: bool = True, expanding: bool = False) -> QSpacerItem:
    """创建占位空间

    Args:
        horizontal: 是否水平占位
        expanding: 是否可扩展

    Returns:
        QSpacerItem: 占位空间对象
    """
    if expanding:
        policy = QSizePolicy.Expanding
    else:
        policy = QSizePolicy.Minimum

    if horizontal:
        return QSpacerItem(40, 20, policy, QSizePolicy.Minimum)
    else:
        return QSpacerItem(20, 40, QSizePolicy.Minimum, policy)


def set_font_size(widget: QWidget, size: int, bold: bool = False) -> None:
    """设置控件字体大小

    Args:
        widget: 目标控件
        size: 字体大小
        bold: 是否加粗
    """
    font = widget.font()
    font.setPointSize(size)
    font.setBold(bold)
    widget.setFont(font)


def show_info_dialog(parent: QWidget, title: str, message: str) -> None:
    """显示信息对话框

    Args:
        parent: 父窗口
        title: 标题
        message: 消息内容
    """
    QMessageBox.information(parent, title, message, QMessageBox.Ok)


def show_warning_dialog(parent: QWidget, title: str, message: str) -> None:
    """显示警告对话框

    Args:
        parent: 父窗口
        title: 标题
        message: 消息内容
    """
    QMessageBox.warning(parent, title, message, QMessageBox.Ok)


def show_error_dialog(parent: QWidget, title: str, message: str) -> None:
    """显示错误对话框

    Args:
        parent: 父窗口
        title: 标题
        message: 消息内容
    """
    QMessageBox.critical(parent, title, message, QMessageBox.Ok)


def show_question_dialog(parent: QWidget, title: str, message: str) -> bool:
    """显示询问对话框

    Args:
        parent: 父窗口
        title: 标题
        message: 消息内容

    Returns:
        bool: 用户是否确认
    """
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes


def create_loading_indicator(parent: Optional[QWidget] = None) -> QProgressDialog:
    """创建加载进度指示器

    Args:
        parent: 父窗口

    Returns:
        QProgressDialog: 进度对话框
    """
    progress = QProgressDialog("正在处理中...", "取消", 0, 0, parent)
    progress.setWindowModality(Qt.WindowModal)
    progress.setWindowTitle("请稍候")
    progress.setCancelButton(None)  # 移除取消按钮
    progress.setMinimumDuration(0)  # 立即显示

    # 设置为无限进度条
    progress.setRange(0, 0)

    return progress


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        str: 格式化后的大小字符串
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def validate_url(url: str) -> bool:
    """验证URL格式

    Args:
        url: URL字符串

    Returns:
        bool: 是否有效
    """
    url_pattern = re.compile(
        r'^https?:://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式

    Args:
        api_key: API密钥字符串

    Returns:
        bool: 是否有效
    """
    if not api_key or not api_key.strip():
        return False

    # 简单验证：长度至少20个字符，包含字母和数字
    stripped_key = api_key.strip()
    if len(stripped_key) < 20:
        return False

    has_letter = any(c.isalpha() for c in stripped_key)
    has_digit = any(c.isdigit() for c in stripped_key)

    return has_letter and has_digit


def create_label_with_help(parent: QWidget, text: str, tooltip: str) -> QWidget:
    """创建带帮助信息的标签

    Args:
        parent: 父控件
        text: 标签文本
        tooltip: 帮助信息

    Returns:
        QWidget: 包含标签和帮助按钮的容器控件
    """
    container = QWidget(parent)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)

    label = QLabel(text)
    layout.addWidget(label)

    help_button = QLabel("ⓘ")
    help_button.setStyleSheet("""
        QLabel {
            color: #2196f3;
            font-weight: bold;
            font-size: 10pt;
            padding: 0px 4px;
            border-radius: 10px;
            background-color: #e3f2fd;
        }
        QLabel:hover {
            background-color: #bbdefb;
        }
    """)
    help_button.setToolTip(tooltip)
    layout.addWidget(help_button)

    return container


def create_progress_bar_with_label(parent: QWidget, label_text: str) -> Tuple[QLabel, QProgressBar]:
    """创建带标签的进度条

    Args:
        parent: 父控件
        label_text: 标签文本

    Returns:
        Tuple[QLabel, QProgressBar]: 标签和进度条
    """
    from PySide6.QtWidgets import QProgressBar

    container = QWidget(parent)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    label = QLabel(label_text)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    layout.addWidget(progress_bar)

    return label, progress_bar


def create_info_panel(parent: QWidget, title: str, content: str, icon: str = "ℹ️") -> QWidget:
    """创建信息面板

    Args:
        parent: 父控件
        title: 面板标题
        content: 面板内容
        icon: 图标

    Returns:
        QWidget: 信息面板控件
    """
    panel = QFrame(parent)
    panel.setStyleSheet("""
        QFrame {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
        }
    """)

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(10, 10, 10, 10)

    # 标题行
    header_layout = QHBoxLayout()

    icon_label = QLabel(icon)
    icon_label.setStyleSheet("font-size: 16pt;")
    header_layout.addWidget(icon_label)

    title_label = QLabel(title)
    title_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #495057;")
    header_layout.addWidget(title_label)

    header_layout.addStretch()
    layout.addLayout(header_layout)

    # 内容
    content_label = QLabel(content)
    content_label.setWordWrap(True)
    content_label.setStyleSheet("color: #6c757d; margin-top: 5px;")
    layout.addWidget(content_label)

    return panel


def animate_fade_in(widget: QWidget, duration: int = 300) -> None:
    """淡入动画效果

    Args:
        widget: 目标控件
        duration: 动画持续时间(毫秒)
    """
    from PySide6.QtWidgets import QGraphicsOpacityEffect
    from PySide6.QtCore import QPropertyAnimation

    # 设置透明度效果
    opacity_effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(opacity_effect)

    # 创建动画
    animation = QPropertyAnimation(opacity_effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)

    # 启动动画
    animation.start()


def truncate_filename(filename: str, max_length: int = 30) -> str:
    """截断文件名以适应显示

    Args:
        filename: 文件名
        max_length: 最大长度

    Returns:
        str: 截断后的文件名
    """
    if len(filename) <= max_length:
        return filename

    name, ext = os.path.splitext(filename)
    max_name_length = max_length - len(ext) - 3  # 3 for "..."

    if max_name_length <= 0:
        return filename[:max_length]

    return f"{name[:max_name_length]}...{ext}"


def center_window_to_parent(window: QWidget, parent: Optional[QWidget] = None) -> None:
    """将窗口居中到父窗口或屏幕中央

    Args:
        window: 要居中的窗口
        parent: 父窗口，如果为None则居中到屏幕
    """
    if parent and parent.isVisible():
        parent_geometry = parent.geometry()
        window_geometry = window.geometry()

        x = parent_geometry.x() + (parent_geometry.width() - window_geometry.width()) // 2
        y = parent_geometry.y() + (parent_geometry.height() - window_geometry.height()) // 2
    else:
        # 居中到屏幕
        screen = window.screen() if hasattr(window, 'screen') else None
        if screen is None:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()

        screen_geometry = screen.geometry()
        window_geometry = window.geometry()

        x = screen_geometry.x() + (screen_geometry.width() - window_geometry.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_geometry.height()) // 2

    window.move(x, y)