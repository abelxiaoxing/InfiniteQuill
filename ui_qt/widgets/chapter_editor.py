# ui_qt/widgets/chapter_editor.py
# -*- coding: utf-8 -*-
"""
章节编辑器组件
提供章节内容的查看、编辑、管理等功能的现代化界面
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QFrame, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QTabWidget, QProgressBar
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor, QAction, QTextDocument

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)


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
        self.setup_ui()
        self.setup_editor_actions()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建标题
        title_label = QLabel("📝 章节编辑器")
        set_font_size(title_label, 14, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 6px; margin-bottom: 10px;")
        layout.addWidget(title_label)

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
        nav_group = QGroupBox("📚 章节导航")
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
        list_group = QGroupBox("📋 章节列表")
        list_layout = QVBoxLayout(list_group)

        # 视图切换
        view_layout = QHBoxLayout()
        self.list_view_btn = QPushButton("📄")
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.setChecked(True)
        self.list_view_btn.clicked.connect(lambda: self.switch_view("list"))
        view_layout.addWidget(self.list_view_btn)

        self.tree_view_btn = QPushButton("🌲")
        self.tree_view_btn.setCheckable(True)
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
        action_group = QGroupBox("⚡ 快捷操作")
        action_layout = QVBoxLayout(action_group)

        self.add_chapter_btn = QPushButton("➕ 新增章节")
        self.add_chapter_btn.clicked.connect(self.add_chapter)
        action_layout.addWidget(self.add_chapter_btn)

        self.delete_chapter_btn = QPushButton("🗑️ 删除章节")
        self.delete_chapter_btn.clicked.connect(self.delete_chapter)
        action_layout.addWidget(self.delete_chapter_btn)

        self.reorder_btn = QPushButton("🔄 调整顺序")
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

        self.status_label = QLabel("✏️ 编辑中")
        self.status_label.setStyleSheet("padding: 2px 8px; background-color: #fff3cd; color: #856404; border-radius: 3px;")
        info_layout.addWidget(self.status_label)

        layout.addWidget(info_bar)

        # 主编辑器
        self.chapter_editor = QTextEdit()
        self.chapter_editor.setPlaceholderText("在这里开始写作你的章节内容...\n\n提示: 可以使用工具栏中的格式化工具来美化文本。")
        self.chapter_editor.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.chapter_editor)

        self.editor_tabs.addTab(edit_widget, "✏️ 编辑")

    def create_preview_tab(self):
        """创建预览标签页"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)

        # 预览工具栏
        preview_toolbar = QHBoxLayout()
        self.refresh_preview_btn = QPushButton("🔄 刷新预览")
        self.refresh_preview_btn.clicked.connect(self.refresh_preview)
        preview_toolbar.addWidget(self.refresh_preview_btn)

        self.export_preview_btn = QPushButton("📤 导出预览")
        self.export_preview_btn.clicked.connect(self.export_preview)
        preview_toolbar.addWidget(self.export_preview_btn)

        preview_toolbar.addStretch()
        layout.addLayout(preview_toolbar)

        # 预览区域
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("预览内容将在此显示...")
        layout.addWidget(self.preview_area)

        self.editor_tabs.addTab(preview_widget, "👁️ 预览")

    def create_metadata_tab(self):
        """创建元信息标签页"""
        metadata_widget = QWidget()
        layout = QVBoxLayout(metadata_widget)
        layout.setSpacing(10)

        # 基本信息
        basic_group = QGroupBox("📋 基本信息")
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
        notes_group = QGroupBox("📝 备注")
        notes_layout = QVBoxLayout(notes_group)

        self.chapter_notes = QTextEdit()
        self.chapter_notes.setMaximumHeight(100)
        self.chapter_notes.setPlaceholderText("添加关于此章节的备注...")
        notes_layout.addWidget(self.chapter_notes)

        layout.addWidget(notes_group)
        layout.addStretch()

        self.editor_tabs.addTab(metadata_widget, "📊 信息")

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
        self.insert_image_btn = QPushButton("🖼️")
        self.insert_image_btn.clicked.connect(self.insert_image)
        toolbar_layout.addWidget(self.insert_image_btn)

        self.insert_link_btn = QPushButton("🔗")
        self.insert_link_btn.clicked.connect(self.insert_link)
        toolbar_layout.addWidget(self.insert_link_btn)

        toolbar_layout.addStretch()

        # 保存按钮
        self.save_btn = QPushButton("💾 保存章节")
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

        self.auto_save_label = QLabel("💾 自动保存: 开启")
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
        self.status_label.setText("✏️ 编辑中")
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
        # 这里实现加载章节的逻辑
        # 暂时模拟加载
        self.chapter_editor.setPlainText(f"第{chapter_number}章的内容...")
        self.chapter_title_edit.setText(f"第{chapter_number}章")
        self.is_modified = False
        self.status_label.setText("💾 已保存")
        self.status_label.setStyleSheet("padding: 2px 8px; background-color: #d4edda; color: #155724; border-radius: 3px;")

    def save_current_chapter(self):
        """保存当前章节"""
        if self.is_modified:
            # 这里实现保存逻辑
            self.is_modified = False
            self.status_label.setText("💾 已保存")
            self.status_label.setStyleSheet("padding: 2px 8px; background-color: #d4edda; color: #155724; border-radius: 3px;")
            self.chapter_saved.emit(self.current_chapter)

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
        # 这里实现添加章节的逻辑
        show_info_dialog(self, "提示", "章节添加功能待实现")

    def delete_chapter(self):
        """删除章节"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除第{self.current_chapter}章吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 这里实现删除逻辑
            show_info_dialog(self, "成功", "章节已删除")

    def reorder_chapters(self):
        """调整章节顺序"""
        show_info_dialog(self, "提示", "章节排序功能待实现")

    def apply_format(self, format_type: str):
        """应用格式"""
        cursor = self.chapter_editor.textCursor()
        if not cursor.hasSelection():
            return

        # 这里实现格式化逻辑
        if format_type == "bold":
            # 粗体
            pass
        elif format_type == "italic":
            # 斜体
            pass
        elif format_type == "underline":
            # 下划线
            pass

    def apply_alignment(self, alignment: str):
        """应用对齐"""
        # 这里实现对齐逻辑
        pass

    def insert_image(self):
        """插入图片"""
        show_info_dialog(self, "提示", "图片插入功能待实现")

    def insert_link(self):
        """插入链接"""
        show_info_dialog(self, "提示", "链接插入功能待实现")

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
        self.current_project_path = project_path
        # 这里实现项目加载逻辑
        self.refresh_chapter_list()

    def refresh_chapter_list(self):
        """刷新章节列表"""
        # 模拟加载章节列表
        self.chapter_selector.clear()
        self.chapter_list.clear()

        for i in range(1, 21):  # 假设20章
            chapter_title = f"第{i}章"
            self.chapter_selector.addItem(chapter_title)
            item = QListWidgetItem(chapter_title)
            self.chapter_list.addItem(item)

        # 更新统计
        self.total_chapters_label.setText(str(self.chapter_selector.count()))
        self.completed_chapters_label.setText("0")  # 这里应该是实际的完成数
        self.total_words_label.setText("0")  # 这里应该是总字数

    def get_current_content(self) -> str:
        """获取当前内容"""
        return self.chapter_editor.toPlainText()

    def set_current_content(self, content: str):
        """设置当前内容"""
        self.chapter_editor.setPlainText(content)
        self.is_modified = False