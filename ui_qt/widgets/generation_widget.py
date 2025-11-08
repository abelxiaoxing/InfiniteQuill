# ui_qt/widgets/generation_widget.py
# -*- coding: utf-8 -*-
"""
生成操作组件
包含小说架构生成、章节蓝图、内容生成等核心功能
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QSplitter, QFrame, QProgressBar
)
from PySide6.QtCore import Signal, Qt, QThread, QTimer
from PySide6.QtGui import QFont

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)


class GenerationWidget(QWidget):
    """生成操作组件"""

    # 信号定义
    generation_started = Signal()
    generation_finished = Signal()
    progress_updated = Signal(int, str)

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.is_generating = False
        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 创建标题
        title_label = QLabel("🚀 小说生成操作")
        set_font_size(title_label, 14, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        # 主题感知的背景色
        title_label.setStyleSheet("""
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            background-color: #e8f5e8; /* 默认浅色主题 */
            color: #333333; /* 默认文字色 */
        """)
        self.title_label = title_label  # 保存引用以便主题切换
        layout.addWidget(title_label)

        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # 左侧：小说设定区域
        left_widget = self.create_novel_settings_widget()
        main_splitter.addWidget(left_widget)

        # 右侧：生成操作区域
        right_widget = self.create_generation_operations_widget()
        main_splitter.addWidget(right_widget)

        # 设置分割器比例
        main_splitter.setSizes([400, 600])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        # 底部状态和日志
        self.create_bottom_section(layout)

    def create_novel_settings_widget(self) -> QWidget:
        """创建小说设定区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 基本设定组
        basic_group = QGroupBox("📖 基本设定")
        basic_layout = QFormLayout(basic_group)

        # 小说标题
        self.novel_title = QLineEdit()
        self.novel_title.setPlaceholderText("输入小说标题...")
        basic_layout.addRow("小说标题:", self.novel_title)

        # 主题
        self.novel_topic = QTextEdit()
        self.novel_topic.setMaximumHeight(60)
        self.novel_topic.setPlaceholderText("输入小说主题和核心创意...")
        basic_layout.addRow("主题描述:", self.novel_topic)

        # 体裁
        self.novel_genre = QComboBox()
        self.novel_genre.addItems([
            "玄幻", "科幻", "都市", "历史", "武侠",
            "言情", "悬疑", "恐怖", "同人", "其他"
        ])
        basic_layout.addRow("体裁:", self.novel_genre)

        # 章节数量
        self.chapter_count = QSpinBox()
        self.chapter_count.setRange(5, 200)
        self.chapter_count.setValue(20)
        basic_layout.addRow("章节数量:", self.chapter_count)

        # 预估字数
        self.word_count = QSpinBox()
        self.word_count.setRange(1000, 100000)
        self.word_count.setValue(3000)
        self.word_count.setSuffix(" 字/章")
        basic_layout.addRow("预估字数:", self.word_count)

        layout.addWidget(basic_group)

        # 高级设定组
        advanced_group = QGroupBox("🎨 高级设定")
        advanced_layout = QVBoxLayout(advanced_group)

        # 世界观设定
        worldview_label = QLabel("世界观设定:")
        worldview_label.setStyleSheet("font-weight: bold;")
        advanced_layout.addWidget(worldview_label)

        self.worldview_text = QTextEdit()
        self.worldview_text.setMaximumHeight(80)
        self.worldview_text.setPlaceholderText("描述小说的世界观背景、时代设定、社会结构等...")
        advanced_layout.addWidget(self.worldview_text)

        # 写作风格
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("写作风格:"))
        self.writing_style = QComboBox()
        self.writing_style.addItems([
            "简洁明快", "细腻描写", "幽默风趣", "严肃深沉",
            "华丽辞藻", "朴实无华", "悬疑紧张", "温馨治愈"
        ])
        style_layout.addWidget(self.writing_style)
        advanced_layout.addLayout(style_layout)

        # 目标读者
        reader_layout = QHBoxLayout()
        reader_layout.addWidget(QLabel("目标读者:"))
        self.target_readers = QComboBox()
        self.target_readers.addItems([
            "青少年", "成人", "全年龄", "女性向", "男性向"
        ])
        reader_layout.addWidget(self.target_readers)
        advanced_layout.addLayout(reader_layout)

        layout.addWidget(advanced_group)

        # 保存路径设置
        path_group = QGroupBox("💾 保存设置")
        path_layout = QFormLayout(path_group)

        path_layout.addRow("保存路径:", self.create_path_selector())

        layout.addWidget(path_group)
        layout.addStretch()

        return widget

    def create_path_selector(self) -> QWidget:
        """创建路径选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.save_path = QLineEdit()
        self.save_path.setPlaceholderText("选择保存路径...")
        layout.addWidget(self.save_path)

        self.browse_btn = QPushButton("📁 浏览")
        self.browse_btn.clicked.connect(self.browse_save_path)
        layout.addWidget(self.browse_btn)

        return widget

    def create_generation_operations_widget(self) -> QWidget:
        """创建生成操作区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 创建操作标签页
        self.operation_tabs = QTabWidget()
        layout.addWidget(self.operation_tabs)

        # 架构生成标签页
        self.create_architecture_tab()

        # 章节规划标签页
        self.create_blueprint_tab()

        # 章节生成标签页
        self.create_chapter_generation_tab()

        # 批量操作标签页
        self.create_batch_operations_tab()

        # 进度显示
        self.create_progress_section(layout)

        return widget

    def create_architecture_tab(self):
        """创建架构生成标签页"""
        arch_widget = QWidget()
        layout = QVBoxLayout(arch_widget)
        layout.setSpacing(15)

        # 操作说明
        info_group = QGroupBox("📋 操作说明")
        info_layout = QVBoxLayout(info_group)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(80)
        info_text.setPlainText("""架构生成将创建小说的基础设定，包括：

• 世界观背景设定
• 主要角色设计
• 核心冲突和主题
• 故事发展脉络
• 整体结构规划

请确保已完善左侧的基本设定后再开始生成。""")
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)

        # 生成选项
        options_group = QGroupBox("⚙️ 生成选项")
        options_layout = QFormLayout(options_group)

        self.include_characters = QCheckBox("包含主要角色设定")
        self.include_characters.setChecked(True)
        options_layout.addRow("", self.include_characters)

        self.include_worldview = QCheckBox("包含详细世界观")
        self.include_worldview.setChecked(True)
        options_layout.addRow("", self.include_worldview)

        self.include_plot_outline = QCheckBox("包含剧情大纲")
        self.include_plot_outline.setChecked(True)
        options_layout.addRow("", self.include_plot_outline)

        layout.addWidget(options_group)

        # 生成按钮
        button_group = QGroupBox("🚀 开始生成")
        button_layout = QHBoxLayout(button_group)

        self.generate_arch_btn = QPushButton("🏗️ 生成小说架构")
        self.generate_arch_btn.clicked.connect(self.generate_architecture)
        self.generate_arch_btn.setStyleSheet("font-weight: bold; padding: 10px; font-size: 11pt;")
        button_layout.addWidget(self.generate_arch_btn)

        layout.addWidget(button_group)

        # 结果显示
        self.arch_result_group = QGroupBox("📄 生成结果")
        arch_layout = QVBoxLayout(self.arch_result_group)

        self.arch_result_text = QTextEdit()
        self.arch_result_text.setReadOnly(True)
        self.arch_result_text.setPlaceholderText("架构生成结果将在此显示...")
        arch_layout.addWidget(self.arch_result_text)

        # 结果操作按钮
        result_btn_layout = QHBoxLayout()

        self.save_arch_btn = QPushButton("💾 保存架构")
        self.save_arch_btn.clicked.connect(self.save_architecture)
        result_btn_layout.addWidget(self.save_arch_btn)

        self.edit_arch_btn = QPushButton("✏️ 编辑架构")
        self.edit_arch_btn.clicked.connect(self.edit_architecture)
        result_btn_layout.addWidget(self.edit_arch_btn)

        self.export_arch_btn = QPushButton("📤 导出架构")
        self.export_arch_btn.clicked.connect(self.export_architecture)
        result_btn_layout.addWidget(self.export_arch_btn)

        result_btn_layout.addStretch()
        arch_layout.addLayout(result_btn_layout)

        layout.addWidget(self.arch_result_group)

        self.operation_tabs.addTab(arch_widget, "🏗️ 架构生成")

    def create_blueprint_tab(self):
        """创建章节规划标签页"""
        blueprint_widget = QWidget()
        layout = QVBoxLayout(blueprint_widget)
        layout.setSpacing(15)

        # 章节概览
        overview_group = QGroupBox("📊 章节概览")
        overview_layout = QGridLayout(overview_group)

        overview_layout.addWidget(QLabel("总章节数:"), 0, 0)
        self.total_chapters_label = QLabel("0")
        overview_layout.addWidget(self.total_chapters_label, 0, 1)

        overview_layout.addWidget(QLabel("已规划:"), 0, 2)
        self.planned_chapters_label = QLabel("0")
        overview_layout.addWidget(self.planned_chapters_label, 0, 3)

        overview_layout.addWidget(QLabel("总字数:"), 1, 0)
        self.total_words_label = QLabel("0")
        overview_layout.addWidget(self.total_words_label, 1, 1)

        overview_layout.addWidget(QLabel("预估完成度:"), 1, 2)
        self.completion_label = QLabel("0%")
        overview_layout.addWidget(self.completion_label, 1, 3)

        layout.addWidget(overview_group)

        # 生成控制
        control_group = QGroupBox("🎛️ 生成控制")
        control_layout = QFormLayout(control_group)

        control_layout.addRow("起始章节:", self.create_chapter_range_selector())

        self.detail_level = QComboBox()
        self.detail_level.addItems(["简要", "标准", "详细"])
        control_layout.addRow("详细程度:", self.detail_level)

        self.generate_chapter_btn = QPushButton("📋 生成章节蓝图")
        self.generate_chapter_btn.clicked.connect(self.generate_chapter_blueprint)
        control_layout.addRow("", self.generate_chapter_btn)

        layout.addWidget(control_group)

        # 章节列表
        list_group = QGroupBox("📝 章节列表")
        list_layout = QVBoxLayout(list_group)

        # 这里应该是一个实际的章节列表控件，暂时用TextEdit代替
        self.chapter_list_text = QTextEdit()
        self.chapter_list_text.setReadOnly(True)
        self.chapter_list_text.setPlaceholderText("章节蓝图将在此显示...")
        list_layout.addWidget(self.chapter_list_text)

        layout.addWidget(list_group)

        self.operation_tabs.addTab(blueprint_widget, "📋 章节规划")

    def create_chapter_generation_tab(self):
        """创建章节生成标签页"""
        chapter_widget = QWidget()
        layout = QVBoxLayout(chapter_widget)
        layout.setSpacing(15)

        # 章节选择
        select_group = QGroupBox("🎯 章节选择")
        select_layout = QHBoxLayout(select_group)

        select_layout.addWidget(QLabel("选择章节:"))
        self.chapter_selector = QComboBox()
        select_layout.addWidget(self.chapter_selector)

        self.refresh_chapters_btn = QPushButton("🔄 刷新")
        self.refresh_chapters_btn.clicked.connect(self.refresh_chapter_list)
        select_layout.addWidget(self.refresh_chapters_btn)

        layout.addWidget(select_group)

        # 生成参数
        params_group = QGroupBox("⚙️ 生成参数")
        params_layout = QFormLayout(params_group)

        self.chapter_word_target = QSpinBox()
        self.chapter_word_target.setRange(500, 20000)
        self.chapter_word_target.setValue(3000)
        self.chapter_word_target.setSuffix(" 字")
        params_layout.addRow("目标字数:", self.chapter_word_target)

        self.include_context = QCheckBox("包含上下文")
        self.include_context.setChecked(True)
        params_layout.addRow("", self.include_context)

        self.consistency_check = QCheckBox("一致性检查")
        self.consistency_check.setChecked(True)
        params_layout.addRow("", self.consistency_check)

        layout.addWidget(params_group)

        # 生成控制
        generate_group = QGroupBox("🚀 生成控制")
        generate_layout = QHBoxLayout(generate_group)

        self.generate_single_btn = QPushButton("📝 生成当前章节")
        self.generate_single_btn.clicked.connect(self.generate_single_chapter)
        generate_layout.addWidget(self.generate_single_btn)

        self.generate_batch_btn = QPushButton("📦 批量生成")
        self.generate_batch_btn.clicked.connect(self.generate_batch_chapters)
        generate_layout.addWidget(self.generate_batch_btn)

        layout.addWidget(generate_group)

        # 内容预览
        preview_group = QGroupBox("👁️ 内容预览")
        preview_layout = QVBoxLayout(preview_group)

        self.chapter_preview = QTextEdit()
        self.chapter_preview.setReadOnly(True)
        self.chapter_preview.setPlaceholderText("章节内容将在此显示...")
        preview_layout.addWidget(self.chapter_preview)

        layout.addWidget(preview_group)

        self.operation_tabs.addTab(chapter_widget, "📝 章节生成")

    def create_batch_operations_tab(self):
        """创建批量操作标签页"""
        batch_widget = QWidget()
        layout = QVBoxLayout(batch_widget)
        layout.setSpacing(15)

        # 知识库导入
        import_group = QGroupBox("📚 知识库导入")
        import_layout = QFormLayout(import_group)

        self.knowledge_file = QLineEdit()
        self.knowledge_file.setPlaceholderText("选择知识文件...")
        import_layout.addRow("知识文件:", self.create_file_selector(self.knowledge_file))

        self.import_knowledge_btn = QPushButton("📥 导入知识库")
        self.import_knowledge_btn.clicked.connect(self.import_knowledge)
        import_layout.addRow("", self.import_knowledge_btn)

        layout.addWidget(import_group)

        # 一致性检查
        consistency_group = QGroupBox("🔍 一致性检查")
        consistency_layout = QVBoxLayout(consistency_group)

        self.check_consistency_btn = QPushButton("🔍 执行一致性检查")
        self.check_consistency_btn.clicked.connect(self.check_consistency)
        consistency_layout.addWidget(self.check_consistency_btn)

        layout.addWidget(consistency_group)

        # 内容优化
        optimize_group = QGroupBox("✨ 内容优化")
        optimize_layout = QVBoxLayout(optimize_group)

        self.optimize_content_btn = QPushButton("✨ 优化选定内容")
        self.optimize_content_btn.clicked.connect(self.optimize_content)
        optimize_layout.addWidget(self.optimize_content_btn)

        layout.addWidget(optimize_group)

        # 数据导出
        export_group = QGroupBox("📤 数据导出")
        export_layout = QFormLayout(export_group)

        self.export_format = QComboBox()
        self.export_format.addItems(["Word文档", "PDF", "TXT", "Markdown"])
        export_layout.addRow("导出格式:", self.export_format)

        self.export_data_btn = QPushButton("📤 导出小说")
        self.export_data_btn.clicked.connect(self.export_novel)
        export_layout.addRow("", self.export_data_btn)

        layout.addWidget(export_group)
        layout.addStretch()

        self.operation_tabs.addTab(batch_widget, "⚙️ 批量操作")

    def create_chapter_range_selector(self) -> QWidget:
        """创建章节范围选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.start_chapter = QSpinBox()
        self.start_chapter.setRange(1, 200)
        self.start_chapter.setValue(1)
        layout.addWidget(self.start_chapter)

        layout.addWidget(QLabel("至"))

        self.end_chapter = QSpinBox()
        self.end_chapter.setRange(1, 200)
        self.end_chapter.setValue(5)
        layout.addWidget(self.end_chapter)

        return widget

    def create_file_selector(self, line_edit: QLineEdit) -> QWidget:
        """创建文件选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(line_edit)

        browse_btn = QPushButton("📁 浏览")
        browse_btn.clicked.connect(lambda: self.browse_file(line_edit))
        layout.addWidget(browse_btn)

        return widget

    def create_progress_section(self, layout: QVBoxLayout):
        """创建进度显示区域"""
        progress_group = QGroupBox("📊 处理进度")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("就绪")
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_group)

    def create_bottom_section(self, layout: QVBoxLayout):
        """创建底部区域"""
        # 创建分割线
        separator = create_separator()
        layout.addWidget(separator)

        # 日志显示
        log_group = QGroupBox("📋 操作日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 9pt;")
        self.log_text.setPlaceholderText("操作日志将在此显示...")
        log_layout.addWidget(self.log_text)

        # 日志控制按钮
        log_control_layout = QHBoxLayout()

        self.clear_log_btn = QPushButton("🗑️ 清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_control_layout.addWidget(self.clear_log_btn)

        log_control_layout.addStretch()

        log_layout.addLayout(log_control_layout)
        layout.addWidget(log_group)

    def load_current_config(self):
        """加载当前配置"""
        # 加载其他参数配置
        other_params = self.config.get("other_params", {})
        if other_params:
            self.novel_title.setText(other_params.get("title", ""))
            self.novel_topic.setText(other_params.get("topic", ""))
            self.novel_genre.setCurrentText(other_params.get("genre", "玄幻"))
            self.chapter_count.setValue(other_params.get("num_chapters", 20))
            self.word_count.setValue(other_params.get("word_number", 3000))
            self.save_path.setText(other_params.get("filepath", ""))

    def browse_save_path(self):
        """浏览保存路径"""
        from PySide6.QtWidgets import QFileDialog

        directory = QFileDialog.getExistingDirectory(
            self, "选择保存路径", self.save_path.text()
        )
        if directory:
            self.save_path.setText(directory)

    def browse_file(self, line_edit: QLineEdit):
        """浏览文件"""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*)"
        )
        if file_path:
            line_edit.setText(file_path)

    def log_message(self, message: str):
        """添加日志消息"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def update_progress(self, value: int, message: str = ""):
        """更新进度"""
        self.progress_bar.setValue(value)
        if message:
            self.progress_label.setText(message)
        self.progress_updated.emit(value, message)

    def generate_architecture(self):
        """生成小说架构"""
        if self.is_generating:
            show_error_dialog(self, "错误", "正在生成中，请等待完成")
            return

        # 验证输入
        if not self.novel_title.text().strip():
            show_error_dialog(self, "错误", "请输入小说标题")
            return

        if not self.novel_topic.toPlainText().strip():
            show_error_dialog(self, "错误", "请输入主题描述")
            return

        self.is_generating = True
        self.generation_started.emit()
        self.generate_arch_btn.setEnabled(False)
        self.log_message("开始生成小说架构...")
        self.update_progress(10, "初始化生成参数...")

        # 这里实现实际的架构生成逻辑
        # 模拟生成过程
        for i in range(1, 101):
            from PySide6.QtCore import QTimer

            def update_step(step):
                self.update_progress(step, f"生成中... {step}%")
                if step == 100:
                    self.complete_architecture_generation()

            QTimer.singleShot(i * 50, lambda s=i: update_step(s))

    def complete_architecture_generation(self):
        """完成架构生成"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_arch_btn.setEnabled(True)

        # 模拟生成的架构内容
        result = f"""# {self.novel_title.text()}

## 世界观设定
时代背景：{self.worldview_text.toPlainText() or "现代都市"}
题材类型：{self.novel_genre.currentText()}
写作风格：{self.writing_style.currentText()}

## 主要角色
1. 主角：张三 - 身份神秘，能力超群
2. 配角：李四 - 主角挚友，性格开朗
3. 反派：王五 - 城市地下势力的首领

## 故事梗概
故事围绕{self.novel_topic.toPlainText()}展开，主角在{self.novel_genre.currentText()}的世界中面临各种挑战...

## 章节规划
总共{self.chapter_count.value()}章，预计{self.chapter_count.value() * self.word_count.value()}字

## 核心主题
{self.novel_topic.toPlainText()}
"""

        self.arch_result_text.setPlainText(result)
        self.log_message("架构生成完成！")
        self.update_progress(100, "架构生成完成")

    def save_architecture(self):
        """保存架构"""
        content = self.arch_result_text.toPlainText()
        if not content.strip():
            show_error_dialog(self, "错误", "没有内容可保存")
            return

        # 这里实现保存逻辑
        self.log_message("架构已保存")
        show_info_dialog(self, "成功", "架构已保存")

    def edit_architecture(self):
        """编辑架构"""
        self.arch_result_text.setReadOnly(False)
        self.edit_arch_btn.setText("💾 保存编辑")
        self.edit_arch_btn.clicked.disconnect()
        self.edit_arch_btn.clicked.connect(self.save_architecture_edits)

    def save_architecture_edits(self):
        """保存架构编辑"""
        self.arch_result_text.setReadOnly(True)
        self.edit_arch_btn.setText("✏️ 编辑架构")
        self.edit_arch_btn.clicked.disconnect()
        self.edit_arch_btn.clicked.connect(self.edit_architecture)

        self.log_message("架构编辑已保存")
        show_info_dialog(self, "成功", "编辑已保存")

    def export_architecture(self):
        """导出架构"""
        # 这里实现导出逻辑
        self.log_message("架构已导出")
        show_info_dialog(self, "成功", "架构已导出")

    def generate_chapter_blueprint(self):
        """生成章节蓝图"""
        self.log_message("开始生成章节蓝图...")
        # 实现章节蓝图生成逻辑

    def refresh_chapter_list(self):
        """刷新章节列表"""
        self.chapter_selector.clear()
        for i in range(1, self.chapter_count.value() + 1):
            self.chapter_selector.addItem(f"第{i}章")
        self.log_message("章节列表已刷新")

    def generate_single_chapter(self):
        """生成单个章节"""
        current_chapter = self.chapter_selector.currentText()
        if not current_chapter:
            show_error_dialog(self, "错误", "请选择章节")
            return

        self.log_message(f"开始生成 {current_chapter}...")
        # 实现单章生成逻辑

    def generate_batch_chapters(self):
        """批量生成章节"""
        self.log_message("开始批量生成章节...")
        # 实现批量生成逻辑

    def import_knowledge(self):
        """导入知识库"""
        self.log_message("导入知识库中...")
        # 实现知识库导入逻辑

    def check_consistency(self):
        """执行一致性检查"""
        self.log_message("执行一致性检查...")
        # 实现一致性检查逻辑

    def optimize_content(self):
        """优化内容"""
        self.log_message("优化内容中...")
        # 实现内容优化逻辑

    def export_novel(self):
        """导出小说"""
        self.log_message("导出小说中...")
        # 实现小说导出逻辑

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
    def update_component_themes(self, theme_name: str):
        """更新组件主题以适配深浅色切换"""
        if theme_name == "dark":
            # 深色主题：更柔和的背景色
            if hasattr(self, 'title_label') and self.title_label:
                self.title_label.setStyleSheet("""
                    padding: 10px;
                    border-radius: 6px;
                    margin-bottom: 10px;
                    background-color: #1b5e20;  /* 深绿色，更柔和 */
                    color: #ffffff;  /* 白色文字 */
                    font-weight: bold;
                    font-size: 14pt;
                """)
        else:
            # 浅色主题：恢复亮绿色
            if hasattr(self, 'title_label') and self.title_label:
                self.title_label.setStyleSheet("""
                    padding: 10px;
                    border-radius: 6px;
                    margin-bottom: 10px;
                    background-color: #e8f5e8;  /* 亮绿色 */
                    color: #333333;  /* 黑色文字 */
                    font-weight: bold;
                    font-size: 14pt;
                """)
