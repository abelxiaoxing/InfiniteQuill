# ui_qt/utils/theme_manager.py
# -*- coding: utf-8 -*-
"""
主题管理器
负责应用程序的主题切换和样式管理
"""

import os
from typing import Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject


class ThemeManager(QObject):
    """主题管理器类"""

    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.theme_cache = {}

    def load_qss_file(self, theme_name: str) -> str:
        """加载QSS样式文件"""
        if theme_name in self.theme_cache:
            return self.theme_cache[theme_name]

        # 样式文件路径
        style_dir = os.path.join(os.path.dirname(__file__), "..", "styles")
        qss_file = os.path.join(style_dir, f"{theme_name}.qss")

        if os.path.exists(qss_file):
            with open(qss_file, 'r', encoding='utf-8') as f:
                qss_content = f.read()
                self.theme_cache[theme_name] = qss_content
                return qss_content
        else:
            # 如果样式文件不存在，返回默认样式
            return self.get_default_style(theme_name)

    def get_default_style(self, theme_name: str) -> str:
        """获取默认样式"""
        if theme_name == "dark":
            return self.get_dark_theme()
        else:
            return self.get_light_theme()

    def get_light_theme(self) -> str:
        """浅色主题样式"""
        return """
        /* ================ 全局样式 ================ */
        QWidget {
            font-family: "Microsoft YaHei UI", "Segoe UI Emoji", "Apple Color Emoji", "JetBrains Mono", "PingFang SC", "Noto Sans CJK SC", "Noto Color Emoji", "Noto Sans Mono", "DejaVu Sans Mono", sans-serif;
            font-size: 9pt;
            background-color: #ffffff;
            color: #333333;
        }

        QMainWindow {
            background-color: #f5f5f5;
        }

        /* ================ 标签页样式 ================ */
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: #ffffff;
        }

        QTabBar::tab {
            background-color: #e1e1e1;
            border: 1px solid #c0c0c0;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
        }

        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }

        /* ================ 按钮样式 ================ */
        QPushButton {
            background-color: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 80px;
            color: #333333;
        }

        QPushButton:hover {
            background-color: #bbdefb;
        }

        QPushButton:pressed {
            background-color: #90caf9;
        }

        QPushButton:disabled {
            background-color: #f5f5f5;
            border-color: #cccccc;
            color: #888888;
        }

        QPushButton[style="primary"] {
            background-color: #2196f3;
            color: white;
            font-weight: bold;
        }

        QPushButton[style="primary"]:hover {
            background-color: #1976d2;
        }

        QPushButton[style="success"] {
            background-color: #4caf50;
            color: white;
        }

        QPushButton[style="success"]:hover {
            background-color: #45a049;
        }

        QPushButton[style="warning"] {
            background-color: #ff9800;
            color: white;
        }

        QPushButton[style="warning"]:hover {
            background-color: #fb8c00;
        }

        QPushButton[style="danger"] {
            background-color: #f44336;
            color: white;
        }

        QPushButton[style="danger"]:hover {
            background-color: #d32f2f;
        }

        /* ================ 输入框样式 ================ */
        QLineEdit, QTextEdit, QPlainTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 6px;
            background-color: #ffffff;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #2196f3;
            outline: none;
        }

        /* ================ 组合框样式 ================ */
        QComboBox {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 6px 24px 6px 8px;
            background-color: #ffffff;
            min-width: 120px;
        }

        QComboBox:focus {
            border-color: #2196f3;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #666;
            margin-right: 8px;
        }

        /* ================ 滑块样式 ================ */
        QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 8px;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #2196f3;
            border: 1px solid #1976d2;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }

        /* ================ 分组框样式 ================ */
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        /* ================ 分割器样式 ================ */
        QSplitter::handle {
            background-color: #d0d0d0;
        }

        QSplitter::handle:horizontal {
            width: 2px;
        }

        QSplitter::handle:vertical {
            height: 2px;
        }

        /* ================ 滚动条样式 ================ */
        QScrollBar:vertical {
            border: none;
            background: #f0f0f0;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:vertical {
            background: #c0c0c0;
            min-height: 20px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        /* ================ 状态栏样式 ================ */
        QStatusBar {
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }

        QStatusBar QLabel {
            padding: 2px 8px;
        }

        /* ================ 进度条样式 ================ */
        QProgressBar {
            border: 1px solid #ddd;
            border-radius: 4px;
            text-align: center;
            background-color: #ffffff;
        }

        QProgressBar::chunk {
            background-color: #2196f3;
            border-radius: 3px;
        }

        /* ================ 菜单样式 ================ */
        QMenuBar {
            background-color: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }

        QMenuBar::item {
            padding: 4px 8px;
            background-color: transparent;
        }

        QMenuBar::item:selected {
            background-color: #e9ecef;
        }

        QMenu {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            padding: 4px 0px;
        }

        QMenu::item {
            padding: 6px 20px;
        }

        QMenu::item:selected {
            background-color: #e3f2fd;
        }

        /* ================ 表格样式 ================ */
        QTableWidget {
            gridline-color: #e0e0e0;
            background-color: #ffffff;
            selection-background-color: #e3f2fd;
        }

        QTableWidget::item {
            padding: 4px 8px;
        }

        QTableWidget::item:selected {
            background-color: #bbdefb;
        }

        QHeaderView::section {
            background-color: #f5f5f5;
            padding: 4px 8px;
            border: 1px solid #e0e0e0;
            font-weight: bold;
        }

        /* ================ 树形控件样式 ================ */
        QTreeWidget {
            background-color: #ffffff;
            selection-background-color: #e3f2fd;
            alternate-background-color: #f9f9f9;
        }

        QTreeWidget::item {
            padding: 2px 4px;
        }

        QTreeWidget::item:selected {
            background-color: #bbdefb;
        }

        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {
            border-image: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDhMOCA0TDQgOEw4IDEyTDEyIDhaIiBmaWxsPSIjNjY2NjY2Ii8+Cjwvc3ZnPgo=);
        }

        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {
            border-image: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDZMOCAxMEw0IDZIOVoiIGZpbGw9IiM2NjY2NjYiLz4KPC9zdmc+Cg==);
        }

        /* ================ 工具提示样式 ================ */
        QToolTip {
            background-color: #ffffe0;
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 4px 6px;
            font-size: 8pt;
        }

        /* ================ 主题感知分隔线样式 ================ */
        QFrame#ThemeAwareSeparator {
            background-color: #c0c0c0;
        }

        /* ================ 角色操作组样式 ================ */
        QFrame#RoleActionGroup {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }

        /* 角色操作按钮专用样式 - 浅色主题 */
        QFrame#RoleActionGroup QPushButton {
            background-color: #e3f2fd;
            border: 1px solid #2196f3;
            color: #333333;
            padding: 6px 12px;
            border-radius: 4px;
            min-width: 80px;
        }

        QFrame#RoleActionGroup QPushButton:hover {
            background-color: #bbdefb;
        }

        QFrame#RoleActionGroup QPushButton:pressed {
            background-color: #90caf9;
        }

        QFrame#RoleActionGroup QPushButton:disabled {
            background-color: #f5f5f5;
            border-color: #cccccc;
            color: #888888;
        }

        /* ================ 信息面板样式 - 浅色主题 ================ */
        QFrame#InfoPanel {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
            color: #333333;
        }

        QFrame#InfoPanel QLabel {
            color: #495057;
        }

        QFrame#InfoPanel QLabel#InfoPanelContent {
            color: #6c757d;
        }

        /* ================ 角色列表样式 - 浅色主题 ================ */
        QListWidget#RoleListWidget {
            border: none;
            background-color: transparent;
            outline: none;
        }

        QListWidget#RoleListWidget::item {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            margin: 0px;
            color: #333333;
        }

        QListWidget#RoleListWidget::item:hover {
            background-color: #f5f5f5;
        }

        QListWidget#RoleListWidget::item:selected {
            background-color: #e3f2fd;
            border-left: 4px solid #1976d2;
        }

        /* ================ 状态指示器样式 - 浅色主题 ================ */
        QLabel#GenerationStatusIndicator {
            padding: 2px 8px;
            border-radius: 3px;
            background-color: #e8f5e8;
            color: #2e7d2e;
        }

        QLabel#GenerationStatusIndicator[status="generating"] {
            background-color: #fff3cd;
            color: #856404;
            font-weight: bold;
        }

        QLabel#GenerationStatusIndicator[status="idle"] {
            background-color: #e8f5e8;
            color: #2e7d2e;
            font-weight: normal;
        }

        /* ================ 导入标题样式 - 浅色主题 ================ */
        QLabel#ImportTitleLabel {
            background-color: #e8f5e8;
            color: #2e7d2e;
        }

        /* ================ 应用设置标题样式 - 浅色主题 ================ */
        QLabel#AppSettingsTitle {
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
            margin-bottom: 10px;
            color: #333333;
            font-weight: bold;
        }

        /* ================ 主题预览框架 - 浅色主题 ================ */
        QFrame#ThemePreviewFrame {
            border: 2px solid #ddd;
            border-radius: 8px;
            background-color: #ffffff;
            color: #333333;
            padding: 20px;
        }

        /* ================ 主题预览标题 - 浅色主题 ================ */
        QLabel#ThemePreviewTitle {
            font-weight: bold;
            font-size: 12pt;
            color: #333333;
        }

        /* ================ 架构状态标签 - 浅色主题 ================ */
        QLabel#ArchitectureStatusLabel {
            color: #666666;
            font-style: italic;
        }

        QLabel#ArchitectureStatusLabel[status="success"] {
            color: #27ae60;
            font-style: normal;
        }

        QLabel#ArchitectureStatusLabel[status="warning"] {
            color: #f39c12;
            font-style: normal;
        }

        /* ================ 主窗口组件标题 - 浅色主题 ================ */
        /* 生成组件标题 */
        QLabel#GenerationWidgetTitle {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #e8f5e8;
            color: #333333;
            font-weight: bold;
            font-size: 14pt;
        }

        /* 章节编辑器标题 */
        QLabel#ChapterEditorTitle {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #e3f2fd;
            color: #333333;
            font-weight: bold;
            font-size: 14pt;
        }

        /* 角色管理器标题 */
        QLabel#RoleManagerTitle {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #f3e5f5;
            color: #333333;
            font-weight: bold;
            font-size: 14pt;
        }

        /* ================ 状态栏 - 浅色主题 ================ */
        QStatusBar {
            background-color: #f0f0f0;
            color: #333333;
            border-top: 1px solid #ddd;
        }

        QStatusBar::item {
            border: none;
        }
        """

    def get_dark_theme(self) -> str:
        """深色主题样式"""
        return """
        /* ================ 全局样式 ================ */
        QWidget {
            font-family: "Microsoft YaHei UI", "Segoe UI Emoji", "Apple Color Emoji", "JetBrains Mono", "PingFang SC", "Noto Sans CJK SC", "Noto Color Emoji", "Noto Sans Mono", "DejaVu Sans Mono", sans-serif;
            font-size: 9pt;
            background-color: #2d2d2d;
            color: #ffffff;
        }

        QMainWindow {
            background-color: #1e1e1e;
        }

        /* ================ 标签页样式 ================ */
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #2d2d2d;
        }

        QTabBar::tab {
            background-color: #3d3d3d;
            border: 1px solid #404040;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background-color: #2d2d2d;
            border-bottom-color: #2d2d2d;
        }

        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }

        /* ================ 按钮样式 ================ */
        QPushButton {
            background-color: #1e88e5;
            border: 1px solid #1976d2;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 80px;
            color: #ffffff;
        }

        QPushButton:hover {
            background-color: #1565c0;
        }

        QPushButton:pressed {
            background-color: #0d47a1;
        }

        QPushButton:disabled {
            background-color: #424242;
            border-color: #616161;
            color: #888888;
        }

        QPushButton[style="primary"] {
            background-color: #2196f3;
            color: white;
            font-weight: bold;
        }

        QPushButton[style="primary"]:hover {
            background-color: #1976d2;
        }

        QPushButton[style="success"] {
            background-color: #43a047;
            color: white;
        }

        QPushButton[style="success"]:hover {
            background-color: #388e3c;
        }

        QPushButton[style="warning"] {
            background-color: #fb8c00;
            color: white;
        }

        QPushButton[style="warning"]:hover {
            background-color: #ef6c00;
        }

        QPushButton[style="danger"] {
            background-color: #e53935;
            color: white;
        }

        QPushButton[style="danger"]:hover {
            background-color: #d32f2f;
        }

        /* ================ 输入框样式 ================ */
        QLineEdit, QTextEdit, QPlainTextEdit {
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px;
            background-color: #3d3d3d;
            color: #ffffff;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #2196f3;
            outline: none;
        }

        /* ================ 组合框样式 ================ */
        QComboBox {
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px 24px 6px 8px;
            background-color: #3d3d3d;
            color: #ffffff;
            min-width: 120px;
        }

        QComboBox:focus {
            border-color: #2196f3;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #ffffff;
            margin-right: 8px;
        }

        QComboBox QAbstractItemView {
            background-color: #3d3d3d;
            color: #ffffff;
            selection-background-color: #2196f3;
            border: 1px solid #555;
        }

        /* ================ 滑块样式 ================ */
        QSlider::groove:horizontal {
            border: 1px solid #555;
            background: #3d3d3d;
            height: 8px;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #2196f3;
            border: 1px solid #1976d2;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }

        /* ================ 分组框样式 ================ */
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: #ffffff;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #ffffff;
        }

        /* ================ 分割器样式 ================ */
        QSplitter::handle {
            background-color: #555555;
        }

        QSplitter::handle:horizontal {
            width: 2px;
        }

        QSplitter::handle:vertical {
            height: 2px;
        }

        /* ================ 滚动条样式 ================ */
        QScrollBar:vertical {
            border: none;
            background: #2d2d2d;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:vertical {
            background: #555555;
            min-height: 20px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #777777;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        /* ================ 状态栏样式 ================ */
        QStatusBar {
            background-color: #212121;
            border-top: 1px solid #404040;
            color: #ffffff;
        }

        QStatusBar QLabel {
            padding: 2px 8px;
            color: #ffffff;
        }

        /* ================ 进度条样式 ================ */
        QProgressBar {
            border: 1px solid #555;
            border-radius: 4px;
            text-align: center;
            background-color: #3d3d3d;
            color: #ffffff;
        }

        QProgressBar::chunk {
            background-color: #2196f3;
            border-radius: 3px;
        }

        /* ================ 菜单样式 ================ */
        QMenuBar {
            background-color: #212121;
            border-bottom: 1px solid #404040;
            color: #ffffff;
        }

        QMenuBar::item {
            padding: 4px 8px;
            background-color: transparent;
            color: #ffffff;
        }

        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }

        QMenu {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            padding: 4px 0px;
            color: #ffffff;
        }

        QMenu::item {
            padding: 6px 20px;
        }

        QMenu::item:selected {
            background-color: #1e88e5;
        }

        /* ================ 表格样式 ================ */
        QTableWidget {
            gridline-color: #404040;
            background-color: #2d2d2d;
            selection-background-color: #1e88e5;
            color: #ffffff;
        }

        QTableWidget::item {
            padding: 4px 8px;
        }

        QTableWidget::item:selected {
            background-color: #1976d2;
        }

        QHeaderView::section {
            background-color: #3d3d3d;
            padding: 4px 8px;
            border: 1px solid #404040;
            font-weight: bold;
            color: #ffffff;
        }

        /* ================ 树形控件样式 ================ */
        QTreeWidget {
            background-color: #2d2d2d;
            selection-background-color: #1e88e5;
            alternate-background-color: #3a3a3a;
            color: #ffffff;
        }

        QTreeWidget::item {
            padding: 2px 4px;
        }

        QTreeWidget::item:selected {
            background-color: #1976d2;
        }

        /* ================ 工具提示样式 ================ */
        QToolTip {
            background-color: #3d3d3d;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 4px 6px;
            font-size: 8pt;
            color: #ffffff;
        }

        /* ================ 主题感知分隔线样式 ================ */
        QFrame#ThemeAwareSeparator {
            background-color: #555555;
        }

        /* ================ 角色操作组样式 ================ */
        QFrame#RoleActionGroup {
            background-color: #2d2d2d;
            padding: 10px;
            border-radius: 5px;
        }

        /* 角色操作按钮专用样式 - 暗色主题 */
        QFrame#RoleActionGroup QPushButton {
            background-color: #3d3d3d;
            border: 1px solid #555555;
            color: #ffffff;
            padding: 6px 12px;
            border-radius: 4px;
            min-width: 80px;
        }

        QFrame#RoleActionGroup QPushButton:hover {
            background-color: #4a4a4a;
            border-color: #2196f3;
        }

        QFrame#RoleActionGroup QPushButton:pressed {
            background-color: #2a2a2a;
        }

        QFrame#RoleActionGroup QPushButton:disabled {
            background-color: #424242;
            border-color: #616161;
            color: #888888;
        }

        /* ================ 信息面板样式 - 暗色主题 ================ */
        QFrame#InfoPanel {
            background-color: #2d2d2d;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 10px;
            color: #ffffff;
        }

        QFrame#InfoPanel QLabel {
            color: #ffffff;
        }

        QFrame#InfoPanel QLabel#InfoPanelContent {
            color: #cccccc;
        }

        /* ================ 角色列表样式 - 暗色主题 ================ */
        QListWidget#RoleListWidget {
            border: none;
            background-color: transparent;
            outline: none;
        }

        QListWidget#RoleListWidget::item {
            padding: 12px;
            border-bottom: 1px solid #555555;
            margin: 0px;
            color: #ffffff;
        }

        QListWidget#RoleListWidget::item:hover {
            background-color: #4a4a4a;
        }

        QListWidget#RoleListWidget::item:selected {
            background-color: #1e88e5;
            border-left: 4px solid #1976d2;
        }

        /* ================ 状态指示器样式 - 暗色主题 ================ */
        QLabel#GenerationStatusIndicator {
            padding: 2px 8px;
            border-radius: 3px;
            background-color: #43a047;
            color: #ffffff;
        }

        QLabel#GenerationStatusIndicator[status="generating"] {
            background-color: #ffa726;
            color: #000000;
            font-weight: bold;
        }

        QLabel#GenerationStatusIndicator[status="idle"] {
            background-color: #43a047;
            color: #ffffff;
            font-weight: normal;
        }

        /* ================ 导入标题样式 - 暗色主题 ================ */
        QLabel#ImportTitleLabel {
            background-color: #2d2d2d;
            color: #ffffff;
        }

        /* ================ 应用设置标题样式 - 暗色主题 ================ */
        QLabel#AppSettingsTitle {
            padding: 10px;
            background-color: #2d2d2d;
            border-radius: 6px;
            margin-bottom: 10px;
            color: #ffffff;
            font-weight: bold;
        }

        /* ================ 主题预览框架 - 暗色主题 ================ */
        QFrame#ThemePreviewFrame {
            border: 2px solid #555555;
            border-radius: 8px;
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 20px;
        }

        /* ================ 主题预览标题 - 暗色主题 ================ */
        QLabel#ThemePreviewTitle {
            font-weight: bold;
            font-size: 12pt;
            color: #ffffff;
        }

        /* ================ 架构状态标签 - 暗色主题 ================ */
        QLabel#ArchitectureStatusLabel {
            color: #aaaaaa;
            font-style: italic;
        }

        QLabel#ArchitectureStatusLabel[status="success"] {
            color: #43a047;
            font-style: normal;
        }

        QLabel#ArchitectureStatusLabel[status="warning"] {
            color: #ffa726;
            font-style: normal;
        }

        /* ================ 主窗口组件标题 - 暗色主题 ================ */
        /* 生成组件标题 */
        QLabel#GenerationWidgetTitle {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #1b5e20;
            color: #ffffff;
            font-weight: bold;
            font-size: 14pt;
        }

        /* 章节编辑器标题 */
        QLabel#ChapterEditorTitle {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #1565c0;
            color: #ffffff;
            font-weight: bold;
            font-size: 14pt;
        }

        /* 角色管理器标题 */
        QLabel#RoleManagerTitle {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #6a1b9a;
            color: #ffffff;
            font-weight: bold;
            font-size: 14pt;
        }

        /* ================ 状态栏 - 暗色主题 ================ */
        QStatusBar {
            background-color: #1e1e1e;
            color: #ffffff;
            border-top: 1px solid #555;
        }

        QStatusBar::item {
            border: none;
        }
        """

    def apply_theme(self, window, theme_name: str):
        """应用主题到指定窗口"""
        app = QApplication.instance()
        if app:
            qss_content = self.load_qss_file(theme_name)
            app.setStyleSheet(qss_content)
            self.current_theme = theme_name
            window.current_theme = theme_name

    def get_available_themes(self) -> list:
        """获取可用主题列表"""
        return ["light", "dark"]

    def get_current_theme(self) -> str:
        """获取当前主题"""
        return self.current_theme

    def get_color(self, theme_name: str, color_type: str) -> str:
        """获取主题对应的颜色值

        Args:
            theme_name: 主题名称 ('light' 或 'dark')
            color_type: 颜色类型 ('light_bg', 'dark_bg', 'light_frame', 'warning_bg',
                           'success_bg', 'info_text', 'warning_text', 'success_text', 'primary')

        Returns:
            十六进制颜色值
        """
        colors = {
            "light": {
                "light_bg": "#f8f9fa",
                "medium_bg": "#e9ecef",
                "dark_bg": "#dee2e6",
                "light_frame": "#ffffff",
                "warning_bg": "#fff3cd",
                "warning_text": "#856404",
                "success_bg": "#d4edda",
                "success_text": "#155724",
                "info_text": "#666666",
                "primary": "#4caf50",
                "primary_text": "white",
                "secondary": "#2196F3",
            },
            "dark": {
                "light_bg": "#2d2d2d",
                "medium_bg": "#3d3d3d",
                "dark_bg": "#4a4a4a",
                "light_frame": "#3d3d3d",
                "warning_bg": "#ffa726",
                "warning_text": "#000000",
                "success_bg": "#66bb6a",
                "success_text": "#000000",
                "info_text": "#cccccc",
                "primary": "#43a047",
                "primary_text": "white",
                "secondary": "#1e88e5",
            }
        }

        theme_colors = colors.get(theme_name, colors["light"])
        return theme_colors.get(color_type, colors["light"][color_type])