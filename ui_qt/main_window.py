# ui_qt/main_window.py
# -*- coding: utf-8 -*-
"""
主窗口控制器
基于PySide6的现代化主界面设计
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QStatusBar, QSplitter,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QIcon, QFont, QAction, QPixmap

from .widgets.config_widget import ConfigWidget
from .widgets.generation_widget import GenerationWidget
from .widgets.chapter_editor import ChapterEditor
from .widgets.role_manager import RoleManager
from .widgets.status_bar import StatusBar
from .utils.theme_manager import ThemeManager
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.progress_dialog import ProgressDialog
from config_manager import load_config, save_config
from novel_generator.project_manager import ProjectManager


class MainWindow(QMainWindow):
    """主窗口类 - 现代化PySide6界面"""

    # 信号定义
    config_changed = Signal(dict)
    generation_started = Signal()
    generation_finished = Signal()

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # 使用系统用户配置目录
        self.config = load_config() or {}
        self.theme_manager = ThemeManager()
        # 初始化项目管理器
        self.project_manager = ProjectManager()

        # 先应用初始主题（在创建组件之前）
        self.apply_initial_theme()

        # 初始化界面
        self.setup_ui()
        self.setup_connections()

        # 初始化状态
        self.current_project_path = ""
        self.is_generating = False

        self.logger.info("主窗口初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        # 窗口基本属性
        self.setWindowTitle("InfiniteQuill v2.0 - PySide6版本")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        # 设置应用图标
        self.set_window_icon()

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 创建分割器
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(False)

        # 添加标签页
        self.create_tabs()

        # 将标签页添加到分割器
        self.main_splitter.addWidget(self.tab_widget)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建状态栏
        self.create_status_bar()

        # 设置分割器比例
        self.main_splitter.setStretchFactor(0, 1)

    def set_window_icon(self):
        """设置窗口图标"""
        icon_paths = [
            "icon.png",
            "icon.ico",
            "assets/icon.png",
            os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break

    def create_tabs(self):
        """创建各个功能标签页"""
        # 生成操作标签页
        self.generation_widget = GenerationWidget(self.config, self)
        self.tab_widget.addTab(self.generation_widget, " 生成操作")

        # 配置管理标签页
        self.config_widget = ConfigWidget(self.config, self)
        self.tab_widget.addTab(self.config_widget, " 配置管理")

        # 章节编辑标签页
        self.chapter_editor = ChapterEditor(self.config, self.theme_manager, self)
        self.tab_widget.addTab(self.chapter_editor, " 章节编辑")

        # 角色管理标签页
        self.role_manager = RoleManager(self.config, self)
        self.tab_widget.addTab(self.role_manager, " 角色管理")

        # 设置标签页工具提示
        self.tab_widget.setTabToolTip(0, "小说架构生成、章节蓝图、内容生成等核心功能")
        self.tab_widget.setTabToolTip(1, "LLM模型配置、API密钥管理、代理设置")
        self.tab_widget.setTabToolTip(2, "章节内容编辑、管理、导出")
        self.tab_widget.setTabToolTip(3, "角色创建、编辑、导入导出")

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_project_action = QAction("新建项目(&N)", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.setStatusTip("创建新的小说项目")
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)

        open_project_action = QAction("打开项目(&O)", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.setStatusTip("打开现有项目")
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)

        file_menu.addSeparator()

        save_config_action = QAction("保存配置(&S)", self)
        save_config_action.setShortcut("Ctrl+S")
        save_config_action.setStatusTip("保存当前配置")
        save_config_action.triggered.connect(self.save_config)
        file_menu.addAction(save_config_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        settings_action = QAction("设置(&S)", self)
        settings_action.setStatusTip("打开设置对话框")
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # 主题菜单
        theme_menu = menubar.addMenu("主题(&T)")

        light_theme_action = QAction("浅色主题", self)
        light_theme_action.setStatusTip("切换到浅色主题")
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("深色主题", self)
        dark_theme_action.setStatusTip("切换到深色主题")
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于InfiniteQuill")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def setup_connections(self):
        """设置信号连接"""
        # 配置变更信号
        self.config_widget.config_changed.connect(self.on_config_changed)

        # 生成状态信号
        self.generation_widget.generation_started.connect(self.on_generation_started)
        self.generation_widget.generation_finished.connect(self.on_generation_finished)

        # 标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def apply_initial_theme(self):
        """应用初始主题（在创建组件之前调用）"""
        theme_name = self.config.get("theme", "light")
        # 先应用到QApplication
        self.theme_manager.apply_theme(self, theme_name)

        # 确保所有组件初始化后再次更新（解决深色模式启动问题）
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.post_theme_init)

    def post_theme_init(self):
        """主题应用完成后的初始化"""
        # 更新章节编辑器的主题样式
        if hasattr(self, 'chapter_editor'):
            self.chapter_editor.update_theme_styles()

        # 更新状态栏的主题显示
        if hasattr(self, 'status_bar'):
            theme_name = self.config.get("theme", "light")
            self.status_bar.update_theme_display(theme_name)

    def apply_theme(self):
        """应用主题"""
        theme_name = self.config.get("theme", "light")
        self.theme_manager.apply_theme(self, theme_name)
        # 不再需要update_component_themes，所有样式都通过ThemeManager管理
        # 移除主窗口的内联QSS，避免覆盖ThemeManager的样式
        # 移除对各个组件的主题更新，依赖ThemeManager的统一管理

    def update_component_themes(self, theme_name: str):
        """更新组件主题以适配深浅色切换
        已废弃：所有主题都通过ThemeManager统一管理，不再需要单独更新
        """
        # 留空，所有主题都通过ThemeManager的app.setStyleSheet()应用
        pass

    def on_config_changed(self, new_config: Dict[str, Any]):
        """配置变更处理"""
        self.config.update(new_config)
        self.config_changed.emit(self.config)
        self.status_bar.show_message("配置已更新", 3000)

    def on_generation_started(self):
        """生成开始处理"""
        self.is_generating = True
        self.status_bar.set_generating(True)
        self.status_bar.show_message("开始生成内容...", 0)

    def on_generation_finished(self):
        """生成完成处理"""
        self.is_generating = False
        self.status_bar.set_generating(False)
        self.status_bar.show_message("生成完成", 3000)

    def on_tab_changed(self, index: int):
        """标签页切换处理"""
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.show_message(f"切换到: {tab_name}", 2000)

    def new_project(self):
        """新建项目"""
        # 弹出对话框让用户选择项目位置
        from PySide6.QtWidgets import QInputDialog
        directory = QFileDialog.getExistingDirectory(
            self, "选择项目保存位置", "",
            QFileDialog.ShowDirsOnly
        )
        if directory:
            # 询问项目名称
            project_name, ok = QInputDialog.getText(
                self, "新建项目", "请输入项目名称:", text="未命名小说"
            )
            if not ok or not project_name.strip():
                return

            project_name = project_name.strip()

            # 使用项目管理器创建项目
            try:
                success = self.project_manager.create_project(directory, project_name)
                if success:
                    self.current_project_path = directory
                    self.status_bar.set_project_path(directory)
                    self.status_bar.show_message(f"项目 '{project_name}' 创建成功", 3000)

                    # 初始化子组件
                    self.on_project_created(directory)

                    QMessageBox.information(
                        self, "成功",
                        f"项目 '{project_name}' 创建成功！\n"
                        f"项目路径: {directory}"
                    )
                else:
                    QMessageBox.critical(self, "错误", "创建项目失败！")
            except Exception as e:
                self.logger.error(f"创建项目失败: {e}")
                QMessageBox.critical(self, "错误", f"创建项目时发生错误:\n{str(e)}")

    def open_project(self):
        """打开项目"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择项目文件夹", "",
            QFileDialog.ShowDirsOnly
        )
        if directory:
            # 检查是否是有效的项目
            if not self.project_manager.is_valid_project(directory):
                QMessageBox.warning(
                    self, "无效项目",
                    "选中的文件夹不是有效的项目目录！\n"
                    "请选择一个包含 project.json 文件的项目目录。"
                )
                return

            # 加载项目
            self.load_project(directory)

    def load_project(self, project_path: str):
        """加载项目"""
        try:
            success = self.project_manager.load_project(project_path)
            if success:
                self.current_project_path = project_path
                self.status_bar.set_project_path(project_path)

                # 获取项目信息
                info = self.project_manager.get_project_info()
                project_name = info.get('name', '未知项目')

                # 初始化子组件
                self.on_project_loaded(project_path)

                self.status_bar.show_message(f"项目 '{project_name}' 已加载", 3000)
                self.logger.info(f"项目已加载: {project_path}")

            else:
                QMessageBox.critical(self, "错误", "加载项目失败！")

        except Exception as e:
            self.logger.error(f"加载项目失败: {e}")
            QMessageBox.critical(self, "错误", f"加载项目时发生错误:\n{str(e)}")

    def save_config(self):
        """保存配置到系统用户配置目录"""
        try:
            save_config(self.config, None)
            self.status_bar.show_message("配置已保存到用户配置目录", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")

    def show_settings(self):
        """显示设置对话框"""
        # 传递theme_manager给对话框，确保主题同步
        dialog = SettingsDialog(self.config, self.theme_manager, self)
        if dialog.exec_() == SettingsDialog.Accepted:
            self.config.update(dialog.get_config())
            self.on_config_changed(self.config)

    def change_theme(self, theme_name: str):
        """更改主题"""
        self.config["theme"] = theme_name

        # 同时更新theme_settings中的current_theme，确保配置一致性
        if "theme_settings" not in self.config:
            self.config["theme_settings"] = {}
        self.config["theme_settings"]["current_theme"] = theme_name

        self.apply_theme()

        # 更新章节编辑器的主题样式
        if hasattr(self, 'chapter_editor'):
            self.chapter_editor.update_theme_styles()

        # 更新状态栏的主题显示
        if hasattr(self, 'status_bar'):
            self.status_bar.update_theme_display(theme_name)

        self.save_config()
        self.status_bar.show_message(f"主题已切换到: {theme_name}", 3000)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于InfiniteQuill",
            """InfiniteQuill v2.0 (PySide6版本)

基于大语言模型的智能小说创作工具

特性:
• 现代化PySide6界面，完美中文支持
• 多种LLM服务支持 (OpenAI, DeepSeek, Gemini等)
• 智能小说架构生成与章节管理
• 向量检索确保剧情连贯性
• 角色管理与关系图谱

开发团队: InfiniteQuill Team
Copyright © 2025 All rights reserved."""
        )

    def closeEvent(self, event):
        """关闭事件处理"""
        if self.is_generating:
            reply = QMessageBox.question(
                self, "确认退出",
                "内容生成正在进行中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return

        # 保存配置
        try:
            self.save_config()
        except Exception as e:
            self.logger.warning(f"保存配置失败: {e}")

        event.accept()
        self.logger.info("应用程序已退出")

    def on_project_created(self, project_path: str):
        """项目创建后的初始化处理"""
        try:
            self.logger.info(f"项目创建后初始化: {project_path}")

            # 初始化各个组件的项目上下文
            if hasattr(self, 'chapter_editor') and self.chapter_editor:
                self.chapter_editor.load_project(project_path)

            if hasattr(self, 'role_manager') and self.role_manager:
                self.role_manager.load_project(project_path)

            if hasattr(self, 'generation_widget') and self.generation_widget:
                self.generation_widget.set_project_path(project_path)

            # 刷新所有组件
            if hasattr(self, 'chapter_editor') and self.chapter_editor:
                self.chapter_editor.refresh_chapter_list()

            if hasattr(self, 'role_manager') and self.role_manager:
                self.role_manager.refresh_role_list()

            self.logger.info("项目创建后初始化完成")

        except Exception as e:
            self.logger.error(f"项目创建后初始化失败: {e}")

    def on_project_loaded(self, project_path: str):
        """项目加载后的初始化处理"""
        try:
            self.logger.info(f"项目加载后初始化: {project_path}")

            # 初始化各个组件的项目上下文
            if hasattr(self, 'chapter_editor') and self.chapter_editor:
                self.chapter_editor.load_project(project_path)

            if hasattr(self, 'role_manager') and self.role_manager:
                self.role_manager.load_project(project_path)

            if hasattr(self, 'generation_widget') and self.generation_widget:
                self.generation_widget.set_project_path(project_path)

            # 刷新所有组件
            if hasattr(self, 'chapter_editor') and self.chapter_editor:
                self.chapter_editor.refresh_chapter_list()

            if hasattr(self, 'role_manager') and self.role_manager:
                self.role_manager.refresh_role_list()

            self.logger.info("项目加载后初始化完成")

        except Exception as e:
            self.logger.error(f"项目加载后初始化失败: {e}")