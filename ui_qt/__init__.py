# ui_qt/__init__.py
# -*- coding: utf-8 -*-
"""
PySide6现代化UI模块
为InfiniteQuill提供高性能、美观的图形用户界面
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QFont, QIcon
import sys
import os

def setup_application():
    """设置应用程序基本属性"""
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("InfiniteQuill")
    app.setApplicationDisplayName("InfiniteQuill")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("InfiniteQuill")

    # 设置中文字体和emoji支持
    font = QFont()
    if sys.platform == "win32":
        font.setFamily("Microsoft YaHei UI, Segoe UI Emoji, Apple Color Emoji, JetBrains Mono")
    elif sys.platform == "darwin":
        font.setFamily("PingFang SC, Apple Color Emoji, Noto Sans CJK, Jetbrains Mono")
    else:
        font.setFamily("Noto Sans CJK SC, Noto Color Emoji, Noto Sans Mono, Jetbrains Mono, DejaVu Sans Mono")
    font.setPointSize(9)
    app.setFont(font)

    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 启用高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    return app

# 导出主要组件
from .main_window import MainWindow

__all__ = ['setup_application', 'MainWindow']