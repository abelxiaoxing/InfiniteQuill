# ui_qt/widgets/chapter_editor.py
# -*- coding: utf-8 -*-
"""
章节编辑器组件
提供章节内容的查看、编辑、管理等功能的现代化界面
"""

from typing import Dict, Any, Optional, List
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QFrame, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QTabWidget, QProgressBar, QMenu
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor, QAction, QTextDocument

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)
from novel_generator.data_manager import DataManager


class ChapterEditor(QWidget):
    """章节编辑器组件"""

    # 信号定义
    chapter_selected = Signal(int)
    content_changed = Signal(int, str)
    chapter_saved = Signal(int)

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.current_chapter = 1
        self.current_project_path = ""
        self.is_modified = False
        self.data_manager = None
        self.setup_ui()
        self.setup_editor_actions()
        self.setup_context_menus()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)


        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # 左侧：章节导航和列表
        left_widget = self.create_navigation_widget()
        main_splitter.addWidget(left_widget)

        # 右侧：编辑器区域
        right_widget = self.create_editor_widget()
        main_splitter.addWidget(right_widget)

        # 设置分割器比例
        main_splitter.setSizes([300, 700])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        # 底部状态栏
        self.create_status_bar(layout)

    def create_navigation_widget(self) -> QWidget:
        """创建导航区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 章节导航组
        nav_group = QGroupBox("章节导航")
        nav_layout = QVBoxLayout(nav_group)

        # 章节选择器
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("当前章节:"))
        self.chapter_selector = QComboBox()
        self.chapter_selector.currentIndexChanged.connect(self.on_chapter_selected)
        selector_layout.addWidget(self.chapter_selector)
        nav_layout.addLayout(selector_layout)

        # 导航按钮
        nav_btn_layout = QHBoxLayout()
        self.prev_chapter_btn = QPushButton("⬅️ 上一章")
        self.prev_chapter_btn.clicked.connect(self.prev_chapter)
        nav_btn_layout.addWidget(self.prev_chapter_btn)

        self.next_chapter_btn = QPushButton("下一章 ➡️")
        self.next_chapter_btn.clicked.connect(self.next_chapter)
        nav_btn_layout.addWidget(self.next_chapter_btn)
        nav_layout.addLayout(nav_btn_layout)

        layout.addWidget(nav_group)

        # 章节列表
        list_group = QGroupBox(" 章节列表")
        list_layout = QVBoxLayout(list_group)

        # 视图切换
        view_layout = QHBoxLayout()
        self.list_view_btn = QPushButton("列表")
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.setChecked(True)
        self.list_view_btn.setToolTip("列表视图")
        self.list_view_btn.clicked.connect(lambda: self.switch_view("list"))
        view_layout.addWidget(self.list_view_btn)

        self.tree_view_btn = QPushButton("树形")
        self.tree_view_btn.setCheckable(True)
        self.tree_view_btn.setToolTip("树形视图")
        self.tree_view_btn.clicked.connect(lambda: self.switch_view("tree"))
        view_layout.addWidget(self.tree_view_btn)

        view_layout.addStretch()
        list_layout.addLayout(view_layout)

        # 章节列表控件
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.on_list_item_clicked)
        list_layout.addWidget(self.chapter_list)

        self.chapter_tree = QTreeWidget()
        self.chapter_tree.setHeaderHidden(True)
        self.chapter_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.chapter_tree.hide()
        list_layout.addWidget(self.chapter_tree)

        layout.addWidget(list_group)

        # 章节统计
        stats_group = QGroupBox("📊 统计信息")
        stats_layout = QFormLayout(stats_group)

        self.total_chapters_label = QLabel("0")
        stats_layout.addRow("总章节数:", self.total_chapters_label)

        self.completed_chapters_label = QLabel("0")
        stats_layout.addRow("已完成:", self.completed_chapters_label)

        self.total_words_label = QLabel("0")
        stats_layout.addRow("总字数:", self.total_words_label)

        self.current_words_label = QLabel("0")
        stats_layout.addRow("当前章节:", self.current_words_label)

        layout.addWidget(stats_group)

        # 操作按钮
        action_group = QGroupBox(" 快捷操作")
        action_layout = QVBoxLayout(action_group)

        self.add_chapter_btn = QPushButton("➕ 新增章节")
        self.add_chapter_btn.clicked.connect(self.add_chapter)
        action_layout.addWidget(self.add_chapter_btn)

        self.delete_chapter_btn = QPushButton(" 删除章节")
        self.delete_chapter_btn.clicked.connect(self.delete_chapter)
        action_layout.addWidget(self.delete_chapter_btn)

        self.reorder_btn = QPushButton(" 调整顺序")
        self.reorder_btn.clicked.connect(self.reorder_chapters)
        action_layout.addWidget(self.reorder_btn)

        layout.addWidget(action_group)
        layout.addStretch()

        return widget

    def create_editor_widget(self) -> QWidget:
        """创建编辑器区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 编辑器标签页
        self.editor_tabs = QTabWidget()
        layout.addWidget(self.editor_tabs)

        # 编辑标签页
        self.create_edit_tab()

        # 预览标签页
        self.create_preview_tab()

        # 元信息标签页
        self.create_metadata_tab()

        # 项目概览标签页
        self.create_project_overview_tab()

        # 工具栏
        self.create_toolbar(layout)

        return widget

    def create_edit_tab(self):
        """创建编辑标签页"""
        edit_widget = QWidget()
        layout = QVBoxLayout(edit_widget)
        layout.setSpacing(5)

        # 章节信息栏
        info_bar = QFrame()
        info_bar.setStyleSheet("background-color: #f8f9fa; padding: 5px; border-radius: 3px;")
        info_layout = QHBoxLayout(info_bar)

        self.chapter_title_edit = QLineEdit()
        self.chapter_title_edit.setPlaceholderText("输入章节标题...")
        info_layout.addWidget(self.chapter_title_edit)

        info_layout.addWidget(QLabel("字数:"))
        self.word_count_label = QLabel("0")
        info_layout.addWidget(self.word_count_label)

        self.status_label = QLabel(" 编辑中")
        self.status_label.setStyleSheet("padding: 2px 8px; background-color: #fff3cd; color: #856404; border-radius: 3px;")
        info_layout.addWidget(self.status_label)

        layout.addWidget(info_bar)

        # 主编辑器
        self.chapter_editor = QTextEdit()
        self.chapter_editor.setPlaceholderText("在这里开始写作你的章节内容...\n\n提示: 可以使用工具栏中的格式化工具来美化文本。")
        self.chapter_editor.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.chapter_editor)

        self.editor_tabs.addTab(edit_widget, " 编辑")

    def create_preview_tab(self):
        """创建预览标签页"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)

        # 预览工具栏
        preview_toolbar = QHBoxLayout()
        self.refresh_preview_btn = QPushButton(" 刷新预览")
        self.refresh_preview_btn.clicked.connect(self.refresh_preview)
        preview_toolbar.addWidget(self.refresh_preview_btn)

        self.export_preview_btn = QPushButton(" 导出预览")
        self.export_preview_btn.clicked.connect(self.export_preview)
        preview_toolbar.addWidget(self.export_preview_btn)

        preview_toolbar.addStretch()
        layout.addLayout(preview_toolbar)

        # 预览区域
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("预览内容将在此显示...")
        layout.addWidget(self.preview_area)

        self.editor_tabs.addTab(preview_widget, " 预览")

    def create_metadata_tab(self):
        """创建元信息标签页"""
        metadata_widget = QWidget()
        layout = QVBoxLayout(metadata_widget)
        layout.setSpacing(10)

        # 基本信息
        basic_group = QGroupBox(" 基本信息")
        basic_layout = QFormLayout(basic_group)

        self.chapter_number = QSpinBox()
        self.chapter_number.setRange(1, 999)
        basic_layout.addRow("章节序号:", self.chapter_number)

        self.creation_date = QLineEdit()
        self.creation_date.setReadOnly(True)
        basic_layout.addRow("创建时间:", self.creation_date)

        self.modification_date = QLineEdit()
        self.modification_date.setReadOnly(True)
        basic_layout.addRow("修改时间:", self.modification_date)

        layout.addWidget(basic_group)

        # 内容统计
        content_group = QGroupBox("📊 内容统计")
        content_layout = QFormLayout(content_group)

        self.character_count_label = QLabel("0")
        content_layout.addRow("字符数:", self.character_count_label)

        self.paragraph_count_label = QLabel("0")
        content_layout.addRow("段落数:", self.paragraph_count_label)

        self.reading_time_label = QLabel("0 分钟")
        content_layout.addRow("预估阅读时间:", self.reading_time_label)

        layout.addWidget(content_group)

        # 标签和分类
        tags_group = QGroupBox("🏷️ 标签和分类")
        tags_layout = QVBoxLayout(tags_group)

        self.chapter_tags = QLineEdit()
        self.chapter_tags.setPlaceholderText("输入标签，用逗号分隔...")
        tags_layout.addWidget(self.chapter_tags)

        self.chapter_category = QComboBox()
        self.chapter_category.addItems(["主线剧情", "支线剧情", "回忆", "设定说明", "其他"])
        tags_layout.addWidget(self.chapter_category)

        layout.addWidget(tags_group)

        # 备注
        notes_group = QGroupBox(" 备注")
        notes_layout = QVBoxLayout(notes_group)

        self.chapter_notes = QTextEdit()
        self.chapter_notes.setMaximumHeight(100)
        self.chapter_notes.setPlaceholderText("添加关于此章节的备注...")
        notes_layout.addWidget(self.chapter_notes)

        layout.addWidget(notes_group)
        layout.addStretch()

        self.editor_tabs.addTab(metadata_widget, "📊 信息")

    def create_project_overview_tab(self):
        """创建项目概览标签页"""
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        layout.setSpacing(10)

        # 项目信息组
        project_group = QGroupBox("📋 项目概览")
        project_layout = QVBoxLayout(project_group)
        project_layout.setSpacing(10)

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)

        self.load_summary_btn = QPushButton(" 加载 global_summary.txt")
        self.load_summary_btn.clicked.connect(self.load_global_summary)
        btn_layout.addWidget(self.load_summary_btn)

        self.save_summary_btn = QPushButton(" 保存修改")
        self.save_summary_btn.clicked.connect(self.save_global_summary)
        self.save_summary_btn.setStyleSheet("font-weight: bold; background-color: #4caf50; color: white;")
        btn_layout.addWidget(self.save_summary_btn)

        btn_layout.addStretch()
        project_layout.addLayout(btn_layout)

        # 统计信息
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("字数:"))
        self.summary_word_count = QLabel("0")
        self.summary_word_count.setStyleSheet("font-weight: bold; color: #2196F3;")
        stats_layout.addWidget(self.summary_word_count)
        stats_layout.addStretch()
        project_layout.addLayout(stats_layout)

        # 编辑区域
        self.summary_editor = QTextEdit()
        self.summary_editor.setPlaceholderText("在此编辑全局概览内容...\n\n全局概览是对整个小说项目的总体描述，包括主题、角色关系、剧情发展脉络等关键信息。")
        self.summary_editor.textChanged.connect(self.update_summary_word_count)
        project_layout.addWidget(self.summary_editor)

        layout.addWidget(project_group)

        # 快捷操作
        quick_group = QGroupBox("⚡ 快捷操作")
        quick_layout = QVBoxLayout(quick_group)
        quick_layout.setSpacing(5)

        # 示例模板
        self.use_template_btn = QPushButton(" 插入模板")
        self.use_template_btn.clicked.connect(self.insert_summary_template)
        quick_layout.addWidget(self.use_template_btn)

        self.clear_content_btn = QPushButton(" 清空内容")
        self.clear_content_btn.clicked.connect(lambda: self.summary_editor.clear())
        quick_layout.addWidget(self.clear_content_btn)

        quick_layout.addStretch()
        layout.addWidget(quick_group)

        self.editor_tabs.addTab(overview_widget, "📖 概览")

    def create_toolbar(self, layout: QVBoxLayout):
        """创建工具栏"""
        toolbar_group = QFrame()
        toolbar_group.setStyleSheet("background-color: #f8f9fa; padding: 5px; border-radius: 3px;")
        toolbar_layout = QHBoxLayout(toolbar_group)

        # 格式化按钮
        self.bold_btn = QPushButton("B")
        self.bold_btn.clicked.connect(lambda: self.apply_format("bold"))
        toolbar_layout.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("I")
        self.italic_btn.clicked.connect(lambda: self.apply_format("italic"))
        toolbar_layout.addWidget(self.italic_btn)

        self.underline_btn = QPushButton("U")
        self.underline_btn.clicked.connect(lambda: self.apply_format("underline"))
        toolbar_layout.addWidget(self.underline_btn)

        # 分隔符
        toolbar_layout.addWidget(create_separator("vertical"))

        # 对齐按钮
        self.align_left_btn = QPushButton("⬅")
        self.align_left_btn.clicked.connect(lambda: self.apply_alignment("left"))
        toolbar_layout.addWidget(self.align_left_btn)

        self.align_center_btn = QPushButton("⬌")
        self.align_center_btn.clicked.connect(lambda: self.apply_alignment("center"))
        toolbar_layout.addWidget(self.align_center_btn)

        self.align_right_btn = QPushButton("➡")
        self.align_right_btn.clicked.connect(lambda: self.apply_alignment("right"))
        toolbar_layout.addWidget(self.align_right_btn)

        # 分隔符
        toolbar_layout.addWidget(create_separator("vertical"))

        # 功能按钮
        self.insert_image_btn = QPushButton("图片")
        self.insert_image_btn.setToolTip("插入图片")
        self.insert_image_btn.clicked.connect(self.insert_image)
        toolbar_layout.addWidget(self.insert_image_btn)

        self.insert_link_btn = QPushButton("链接")
        self.insert_link_btn.setToolTip("插入链接")
        self.insert_link_btn.clicked.connect(self.insert_link)
        toolbar_layout.addWidget(self.insert_link_btn)

        toolbar_layout.addStretch()

        # 保存按钮
        self.save_btn = QPushButton(" 保存章节")
        self.save_btn.clicked.connect(self.save_current_chapter)
        self.save_btn.setStyleSheet("font-weight: bold; background-color: #4caf50; color: white;")
        toolbar_layout.addWidget(self.save_btn)

        layout.addWidget(toolbar_group)

    def create_status_bar(self, layout: QVBoxLayout):
        """创建状态栏"""
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #f8f9fa; padding: 5px; border-radius: 3px;")
        status_layout = QHBoxLayout(status_frame)

        self.cursor_position_label = QLabel("行 1, 列 1")
        status_layout.addWidget(self.cursor_position_label)

        status_layout.addWidget(create_separator("vertical"))

        self.selection_info_label = QLabel("未选中")
        status_layout.addWidget(self.selection_info_label)

        status_layout.addStretch()

        self.auto_save_label = QLabel(" 自动保存: 开启")
        status_layout.addWidget(self.auto_save_label)

        layout.addWidget(status_frame)

    def setup_editor_actions(self):
        """设置编辑器操作"""
        # 创建动作
        self.copy_action = QAction("复制", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.chapter_editor.copy)
        self.chapter_editor.addAction(self.copy_action)

        self.paste_action = QAction("粘贴", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.chapter_editor.paste)
        self.chapter_editor.addAction(self.paste_action)

        self.undo_action = QAction("撤销", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.chapter_editor.undo)
        self.chapter_editor.addAction(self.undo_action)

        self.redo_action = QAction("重做", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.chapter_editor.redo)
        self.chapter_editor.addAction(self.redo_action)

        # 连接光标位置变化信号
        self.chapter_editor.cursorPositionChanged.connect(self.update_cursor_position)

    def update_cursor_position(self):
        """更新光标位置"""
        cursor = self.chapter_editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_label.setText(f"行 {line}, 列 {column}")

    def on_chapter_selected(self, index: int):
        """章节选择变更处理"""
        if index >= 0:
            self.current_chapter = index + 1
            self.load_chapter(self.current_chapter)
            self.chapter_selected.emit(self.current_chapter)

    def on_list_item_clicked(self, item: QListWidgetItem):
        """列表项点击处理"""
        index = self.chapter_list.row(item)
        self.chapter_selector.setCurrentIndex(index)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """树形项点击处理"""
        # 处理树形视图点击
        pass

    def on_content_changed(self):
        """内容变更处理"""
        self.is_modified = True
        self.update_word_count()
        self.update_statistics()
        self.status_label.setText(" 编辑中")
        self.status_label.setStyleSheet("padding: 2px 8px; background-color: #fff3cd; color: #856404; border-radius: 3px;")
        self.content_changed.emit(self.current_chapter, self.chapter_editor.toPlainText())

    def update_word_count(self):
        """更新字数统计"""
        text = self.chapter_editor.toPlainText()
        word_count = len(text.replace(" ", ""))  # 中文字数统计
        self.word_count_label.setText(str(word_count))
        self.current_words_label.setText(str(word_count))

    def update_statistics(self):
        """更新统计信息"""
        text = self.chapter_editor.toPlainText()

        # 字符数
        char_count = len(text)
        self.character_count_label.setText(str(char_count))

        # 段落数
        paragraph_count = len([p for p in text.split('\n') if p.strip()])
        self.paragraph_count_label.setText(str(paragraph_count))

        # 预估阅读时间（假设每分钟200字）
        reading_time = max(1, char_count // 200)
        self.reading_time_label.setText(f"{reading_time} 分钟")

    def switch_view(self, view_type: str):
        """切换视图"""
        if view_type == "list":
            self.chapter_list.show()
            self.chapter_tree.hide()
            self.list_view_btn.setChecked(True)
            self.tree_view_btn.setChecked(False)
        else:
            self.chapter_list.hide()
            self.chapter_tree.show()
            self.list_view_btn.setChecked(False)
            self.tree_view_btn.setChecked(True)

    def load_chapter(self, chapter_number: int):
        """加载章节"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        try:
            # 保存当前章节（如果已修改）
            if self.is_modified and self.current_chapter > 0:
                self.save_current_chapter()

            # 加载指定章节
            content = self.data_manager.load_chapter(chapter_number)

            # 如果内容为空，创建一个基本结构
            if not content.strip():
                content = f"\n\n\n# 第{chapter_number}章\n\n在此开始写作...\n"

            # 尝试从内容中提取标题
            title = self._extract_title_from_content(content) or f"第{chapter_number}章"
            content_without_title = self._remove_title_from_content(content)

            # 设置章节内容
            self.chapter_editor.setPlainText(content_without_title)
            self.chapter_title_edit.setText(title)

            # 更新当前章节号
            self.current_chapter = chapter_number

            # 重置修改状态
            self.is_modified = False

            # 更新状态栏
            self.status_label.setText(" 已保存")
            self.status_label.setStyleSheet("padding: 2px 8px; background-color: #d4edda; color: #155724; border-radius: 3px;")

            # 更新统计信息
            self.update_statistics()

        except Exception as e:
            show_error_dialog(self, "错误", f"加载章节失败:\n{str(e)}")

    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """从内容中提取标题"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                return line.lstrip('#').strip()
        return None

    def _remove_title_from_content(self, content: str) -> str:
        """从内容中移除标题行"""
        lines = content.split('\n')
        start_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                start_index = i + 1
        return '\n'.join(lines[start_index:])

    def save_current_chapter(self):
        """保存当前章节"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        if self.current_chapter <= 0:
            show_error_dialog(self, "错误", "请先选择要保存的章节")
            return

        if self.is_modified:
            try:
                # 获取章节内容
                content = self.chapter_editor.toPlainText()
                title = self.chapter_title_edit.text() or f"第{self.current_chapter}章"

                # 保存章节
                self.data_manager.save_chapter(self.current_chapter, content, title)

                # 更新状态
                self.is_modified = False
                self.status_label.setText(" 已保存")
                self.status_label.setStyleSheet("padding: 2px 8px; background-color: #d4edda; color: #155724; border-radius: 3px;")

                # 刷新章节列表中的标题
                self.refresh_chapter_list()

                # 发送信号
                self.chapter_saved.emit(self.current_chapter)

            except Exception as e:
                show_error_dialog(self, "错误", f"保存章节失败:\n{str(e)}")

    def prev_chapter(self):
        """上一章"""
        current_index = self.chapter_selector.currentIndex()
        if current_index > 0:
            self.chapter_selector.setCurrentIndex(current_index - 1)

    def next_chapter(self):
        """下一章"""
        current_index = self.chapter_selector.currentIndex()
        if current_index < self.chapter_selector.count() - 1:
            self.chapter_selector.setCurrentIndex(current_index + 1)

    def add_chapter(self):
        """添加章节"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        from PySide6.QtWidgets import QInputDialog

        # 弹出输入对话框
        chapter_title, ok = QInputDialog.getText(
            self, "添加章节", "请输入章节标题:", text=f"第X章"
        )

        if ok and chapter_title.strip():
            chapter_title = chapter_title.strip()

            try:
                # 获取下一个章节号
                existing_chapters = self.data_manager.list_chapters()
                next_chapter_num = max(existing_chapters) + 1 if existing_chapters else 1

                # 创建空章节内容
                empty_content = f"\n\n\n# {chapter_title}\n\n在此开始写作...\n"

                # 保存章节
                self.data_manager.save_chapter(next_chapter_num, empty_content, chapter_title)

                # 刷新章节列表
                self.refresh_chapter_list()

                # 加载新章节
                self.load_chapter(next_chapter_num)

                # 更新选择器
                self.chapter_selector.setCurrentIndex(next_chapter_num - 1)

                show_info_dialog(self, "成功", f"章节 '{chapter_title}' 已添加")

            except Exception as e:
                show_error_dialog(self, "错误", f"添加章节失败:\n{str(e)}")

    def delete_chapter(self):
        """删除章节"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        if self.current_chapter <= 0:
            show_error_dialog(self, "错误", "请先选择要删除的章节")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除第{self.current_chapter}章吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # 删除章节
                self.data_manager.delete_chapter(self.current_chapter)

                # 刷新章节列表
                self.refresh_chapter_list()

                # 加载下一个章节或上一个章节
                remaining_chapters = self.data_manager.list_chapters()
                if remaining_chapters:
                    # 加载离删除章节最近的章节
                    next_chapter = min(remaining_chapters, key=lambda x: abs(x - self.current_chapter))
                    self.load_chapter(next_chapter)
                    # 更新选择器
                    self.chapter_selector.setCurrentIndex(next_chapter - 1)
                else:
                    # 如果没有章节了，清空编辑器
                    self.chapter_editor.clear()
                    self.chapter_title_edit.clear()
                    self.is_modified = False
                    self.status_label.setText(" 未选择章节")
                    self.status_label.setStyleSheet("padding: 2px 8px; background-color: #f8f9fa; color: #666; border-radius: 3px;")

                show_info_dialog(self, "成功", f"第{self.current_chapter}章已删除")

            except Exception as e:
                show_error_dialog(self, "错误", f"删除章节失败:\n{str(e)}")

    def reorder_chapters(self):
        """调整章节顺序"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, QMessageBox

        # 创建章节重排序对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("章节重排序")
        dialog.setModal(True)
        dialog.resize(400, 500)
        layout = QVBoxLayout(dialog)

        # 说明文字
        label = QLabel("拖拽或使用按钮调整章节顺序:")
        layout.addWidget(label)

        # 章节列表
        chapter_list = QListWidget()
        layout.addWidget(chapter_list)

        # 按钮布局
        button_layout = QHBoxLayout()

        up_btn = QPushButton("上移")
        down_btn = QPushButton("下移")
        cancel_btn = QPushButton("取消")
        confirm_btn = QPushButton("确认")

        button_layout.addWidget(up_btn)
        button_layout.addWidget(down_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(confirm_btn)

        layout.addLayout(button_layout)

        # 加载章节列表
        chapters = self.data_manager.list_chapters()
        for i, chapter_num in enumerate(chapters):
            # 尝试获取章节标题
            content = self.data_manager.load_chapter(chapter_num)
            title = self._extract_title_from_content(content) or f"第{chapter_num}章"
            item = QListWidgetItem(f"{title} (编号: {chapter_num})")
            item.setData(Qt.UserRole, chapter_num)  # 存储章节号
            chapter_list.addItem(item)

        # 上移按钮
        def move_up():
            current_row = chapter_list.currentRow()
            if current_row > 0:
                item = chapter_list.takeItem(current_row)
                chapter_list.insertItem(current_row - 1, item)
                chapter_list.setCurrentRow(current_row - 1)

        # 下移按钮
        def move_down():
            current_row = chapter_list.currentRow()
            if current_row < chapter_list.count() - 1:
                item = chapter_list.takeItem(current_row)
                chapter_list.insertItem(current_row + 1, item)
                chapter_list.setCurrentRow(current_row + 1)

        up_btn.clicked.connect(move_up)
        down_btn.clicked.connect(move_down)
        cancel_btn.clicked.connect(dialog.reject)
        confirm_btn.clicked.connect(dialog.accept)

        # 显示对话框
        if dialog.exec() == QDialog.Accepted:
            # 获取新的顺序
            new_order = []
            for i in range(chapter_list.count()):
                item = chapter_list.item(i)
                if item:
                    chapter_num = item.data(Qt.UserRole)
                    new_order.append(chapter_num)

            # 检查顺序是否改变
            if new_order != chapters:
                try:
                    # 重新编号章节
                    self._reorder_chapters_in_files(new_order)
                    # 刷新章节列表
                    self.refresh_chapter_list()
                    # 重新加载当前章节
                    if self.current_chapter in new_order:
                        self.load_chapter(self.current_chapter)

                    show_info_dialog(self, "成功", "章节顺序已调整")

                except Exception as e:
                    show_error_dialog(self, "错误", f"调整章节顺序失败:\n{str(e)}")

    def _reorder_chapters_in_files(self, new_order: List[int]):
        """重新编号章节文件"""
        if not self.data_manager:
            return

        # 获取所有章节内容
        chapter_contents = {}
        for chapter_num in new_order:
            content = self.data_manager.load_chapter(chapter_num)
            title = self._extract_title_from_content(content) or f"第{chapter_num}章"
            chapter_contents[chapter_num] = (content, title)

        # 删除所有现有章节
        for chapter_num in new_order:
            try:
                self.data_manager.delete_chapter(chapter_num)
            except:
                pass  # 忽略删除失败

        # 按新顺序重新保存
        for i, chapter_num in enumerate(new_order, 1):
            if chapter_num in chapter_contents:
                content, title = chapter_contents[chapter_num]
                self.data_manager.save_chapter(i, content, title)

    def apply_format(self, format_type: str):
        """应用文本格式

        Args:
            format_type: 格式类型，支持 "bold"、"italic"、"underline"
        """
        from PySide6.QtGui import QTextCharFormat

        cursor = self.chapter_editor.textCursor()
        if not cursor.hasSelection():
            return

        # 获取当前选中的文本格式
        format = cursor.charFormat()

        # 根据格式类型应用不同的样式
        if format_type == "bold":
            # 粗体 - 切换粗体状态
            weight = QTextCharFormat.Bold if not format.fontWeight() == QTextCharFormat.Bold else QTextCharFormat.Normal
            format.setFontWeight(weight)
        elif format_type == "italic":
            # 斜体 - 切换斜体状态
            format.setFontItalic(not format.fontItalic())
        elif format_type == "underline":
            # 下划线 - 切换下划线状态
            format.setUnderlineStyle(QTextCharFormat.SingleUnderline if not format.fontUnderline() else QTextCharFormat.NoUnderline)

        # 应用格式到选中的文本
        cursor.mergeCharFormat(format)

    def apply_alignment(self, alignment: str):
        """应用文本对齐

        Args:
            alignment: 对齐方式，支持 "left"、"center"、"right"
        """
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QTextBlockFormat

        cursor = self.chapter_editor.textCursor()

        # 创建段落格式对象
        block_format = QTextBlockFormat()

        # 根据对齐方式设置不同的对齐属性
        if alignment == "left":
            # 左对齐
            block_format.setAlignment(Qt.AlignLeft)
        elif alignment == "center":
            # 居中对齐
            block_format.setAlignment(Qt.AlignCenter)
        elif alignment == "right":
            # 右对齐
            block_format.setAlignment(Qt.AlignRight)

        # 应用段落格式（如果没有选中内容，则应用到当前段落）
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)

        cursor.mergeBlockFormat(block_format)

    def insert_image(self):
        """插入图片到文本中"""
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtGui import QTextImageFormat
        from PySide6.QtCore import QUrl
        import os

        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;所有文件 (*)"
        )

        if file_path:
            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    show_error_dialog(self, "错误", "选择的图片文件不存在")
                    return

                # 获取文件名
                file_name = os.path.basename(file_path)

                # 转换为绝对路径（QUrl需要本地文件路径）
                absolute_path = os.path.abspath(file_path)

                # 创建文本光标
                cursor = self.chapter_editor.textCursor()

                # 创建图片格式
                image_format = QTextImageFormat()
                image_format.setName(QUrl.fromLocalFile(absolute_path).toString())
                image_format.setWidth(300)  # 默认宽度
                image_format.setHeight(200)  # 默认高度

                # 插入图片
                cursor.insertImage(image_format)

                # 在图片后添加换行
                cursor.insertBlock()

                show_info_dialog(self, "成功", f"图片 '{file_name}' 已插入")

            except Exception as e:
                show_error_dialog(self, "错误", f"插入图片失败:\n{str(e)}")

    def insert_link(self):
        """插入链接到文本中"""
        from PySide6.QtWidgets import QInputDialog
        from PySide6.QtGui import QTextCharFormat
        from PySide6.QtCore import QUrl
        import re

        # 打开输入对话框获取URL和链接文本
        url, ok1 = QInputDialog.getText(
            self,
            "插入链接",
            "请输入链接地址 (URL):",
            text="https://"
        )

        if not ok1 or not url:
            return

        # 验证URL格式
        url = url.strip()
        if not re.match(r'^https?://', url) and not re.match(r'^www\.', url):
            show_error_dialog(self, "错误", "请输入有效的URL地址（以http://或https://开头）")
            return

        # 如果没有协议，添加http://
        if not re.match(r'^https?://', url):
            url = "http://" + url

        # 获取链接文本
        link_text, ok2 = QInputDialog.getText(
            self,
            "插入链接",
            "请输入链接显示文本:",
            text="链接文本"
        )

        if not ok2 or not link_text:
            return

        try:
            # 创建文本光标
            cursor = self.chapter_editor.textCursor()

            # 创建链接格式
            link_format = QTextCharFormat()
            link_format.setForeground(Qt.blue)  # 设置蓝色
            link_format.setFontUnderline(True)  # 添加下划线
            link_format.setAnchor(True)  # 标记为锚点
            link_format.setAnchorHref(url)  # 设置链接地址

            # 插入链接文本
            cursor.insertText(link_text, link_format)

            # 在链接后添加空格
            cursor.insertText(" ")

            show_info_dialog(self, "成功", f"链接已插入: {link_text}")

        except Exception as e:
            show_error_dialog(self, "错误", f"插入链接失败:\n{str(e)}")

    def refresh_preview(self):
        """刷新预览"""
        content = self.chapter_editor.toPlainText()
        title = self.chapter_title_edit.text()
        preview = f"# {title}\n\n{content}"
        self.preview_area.setPlainText(preview)

    def export_preview(self):
        """导出预览"""
        show_info_dialog(self, "提示", "预览导出功能待实现")

    def load_project(self, project_path: str):
        """加载项目"""
        try:
            self.current_project_path = project_path
            # 初始化数据管理器
            self.data_manager = DataManager(project_path)

            # 刷新章节列表
            self.refresh_chapter_list()

            # 加载第一个章节（如果存在）
            chapters = self.data_manager.list_chapters()
            if chapters:
                self.load_chapter(chapters[0])
                # 同步章节选择器
                self.chapter_selector.setCurrentIndex(0)

        except Exception as e:
            show_error_dialog(self, "错误", f"加载项目失败:\n{str(e)}")

    def refresh_chapter_list(self):
        """刷新章节列表"""
        # 清空现有列表
        self.chapter_selector.clear()
        self.chapter_list.clear()

        # 如果没有数据管理器，则只显示默认内容
        if not self.data_manager:
            self.total_chapters_label.setText("0")
            self.completed_chapters_label.setText("0")
            self.total_words_label.setText("0")
            return

        try:
            # 从数据管理器获取章节列表
            chapters = self.data_manager.list_chapters()

            # 添加章节到列表
            for chapter_num in chapters:
                chapter_title = f"第{chapter_num}章"
                self.chapter_selector.addItem(chapter_title)
                item = QListWidgetItem(chapter_title)
                self.chapter_list.addItem(item)

            # 更新统计信息
            self.total_chapters_label.setText(str(len(chapters)))
            self.completed_chapters_label.setText(str(len(chapters)))  # 假设所有显示的章节都已完成
            self.total_words_label.setText(str(self.data_manager.load_project_config().get("word_count", 0)))

        except Exception as e:
            show_error_dialog(self, "错误", f"刷新章节列表失败:\n{str(e)}")

    def get_current_content(self) -> str:
        """获取当前内容"""
        return self.chapter_editor.toPlainText()

    def set_current_content(self, content: str):
        """设置当前内容"""
        self.chapter_editor.setPlainText(content)
        self.is_modified = False

    # ========== 项目概览相关方法 ==========

    def load_global_summary(self):
        """加载全局概览文件"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        try:
            # 使用DataManager加载概览
            content = self.data_manager.load_summary()

            # 如果内容为空，设置默认模板
            if not content.strip():
                content = self._get_default_summary_template()

            self.summary_editor.setPlainText(content)
            self.update_summary_word_count()

        except Exception as e:
            show_error_dialog(self, "错误", f"加载全局概览失败:\n{str(e)}")

    def save_global_summary(self):
        """保存全局概览文件"""
        if not self.data_manager:
            show_error_dialog(self, "错误", "请先创建或加载项目")
            return

        try:
            # 获取编辑内容
            content = self.summary_editor.toPlainText().strip()

            # 使用DataManager保存概览
            self.data_manager.save_summary(content)

            # 更新字数统计
            self.update_summary_word_count()

            show_info_dialog(self, "成功", "全局概览已保存")

        except Exception as e:
            show_error_dialog(self, "错误", f"保存全局概览失败:\n{str(e)}")

    def update_summary_word_count(self):
        """更新概览字数统计"""
        text = self.summary_editor.toPlainText()
        # 简单字数统计（去除空白字符）
        count = len(text.replace(" ", "").replace("\n", ""))
        self.summary_word_count.setText(str(count))

    def _get_default_summary_template(self) -> str:
        """获取默认概览模板"""
        return """# 小说项目概览

## 项目基本信息
- **小说标题**: [在此填写小说标题]
- **作品类型**: [如：奇幻、科幻、现代都市、历史等]
- **目标字数**: [预计总字数]
- **目标章节**: [预计章节数]

## 故事主题与核心创意
### 主题
[描述故事的核心主题，如成长、友谊、复仇等]

### 核心创意
[描述独特的故事设定、背景或概念]

### 目标读者
[描述主要读者群体]

## 世界观设定
### 时代背景
[故事发生的时间、地点、社会环境等]

### 世界规则
[魔法系统、科技设定、社会制度等特殊规则]

### 地理环境
[主要场景描述]

## 主要角色
### 主角
- **姓名**:
- **性格特点**:
- **背景故事**:
- **目标与动机**:

### 重要配角
[其他重要角色的简要描述]

### 反派角色
[主要反派的描述]

## 剧情大纲
### 开端
[故事如何开始]

### 发展
[主要冲突的建立和发展]

### 高潮
[故事的转折点和高潮部分]

### 结局
[故事如何结束]

## 章节规划
[简要描述各章节的主要内容和发展脉络]

## 特殊设定
[需要特别注意的设定或伏笔]

## 写作注意事项
[提醒自己在写作过程中需要注意的要点]

---
*此概览文档由 InfiniteQuill AI小说生成器生成*
"""

    def insert_summary_template(self):
        """插入概览模板"""
        try:
            # 获取默认模板
            template = self._get_default_summary_template()

            # 确认是否要插入
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "确认插入",
                "确定要插入概览模板吗？\n这将替换当前内容。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.summary_editor.setPlainText(template)
                self.update_summary_word_count()
                show_info_dialog(self, "成功", "概览模板已插入")

        except Exception as e:
            show_error_dialog(self, "错误", f"插入模板失败:\n{str(e)}")

    def setup_context_menus(self):
        """设置上下文菜单"""
        # 为章节编辑器添加上下文菜单
        self.chapter_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chapter_editor.customContextMenuRequested.connect(self.show_chapter_editor_menu)

        # 为项目概览编辑器添加上下文菜单
        self.summary_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.summary_editor.customContextMenuRequested.connect(self.show_summary_editor_menu)

    def show_chapter_editor_menu(self, position):
        """显示章节编辑器的右键菜单"""
        menu = QMenu(self.chapter_editor)

        # 撤销/重做
        undo_action = QAction("撤销", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.chapter_editor.undo)
        menu.addAction(undo_action)

        redo_action = QAction("重做", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.chapter_editor.redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        # 剪切、复制、粘贴
        cut_action = QAction("剪切", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.chapter_editor.cut)
        menu.addAction(cut_action)

        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.chapter_editor.copy)
        menu.addAction(copy_action)

        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.chapter_editor.paste)
        menu.addAction(paste_action)

        menu.addSeparator()

        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.chapter_editor.selectAll)
        menu.addAction(select_all_action)

        menu.exec_(self.chapter_editor.mapToGlobal(position))

    def show_summary_editor_menu(self, position):
        """显示项目概览编辑器的右键菜单"""
        menu = QMenu(self.summary_editor)

        # 撤销/重做
        undo_action = QAction("撤销", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.summary_editor.undo)
        menu.addAction(undo_action)

        redo_action = QAction("重做", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.summary_editor.redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        # 剪切、复制、粘贴
        cut_action = QAction("剪切", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.summary_editor.cut)
        menu.addAction(cut_action)

        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.summary_editor.copy)
        menu.addAction(copy_action)

        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.summary_editor.paste)
        menu.addAction(paste_action)

        menu.addSeparator()

        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.summary_editor.selectAll)
        menu.addAction(select_all_action)

        menu.exec_(self.summary_editor.mapToGlobal(position))
