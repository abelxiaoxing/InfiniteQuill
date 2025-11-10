# ui_qt/widgets/generation_widget.py
# -*- coding: utf-8 -*-
"""
生成操作组件
包含小说架构生成、章节蓝图、内容生成等核心功能
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
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
    show_error_dialog, create_label_with_help, validate_required
)
from ..utils.tooltip_manager import tooltip_manager

# 导入后端生成器
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from novel_generator.architecture import Novel_architecture_generate
from novel_generator.blueprint import Chapter_blueprint_generate
from novel_generator.chapter import generate_chapter_draft
from llm_adapters import create_llm_adapter
from project_manager import ProjectManager

logger = logging.getLogger(__name__)


class ArchitectureGenerationWorker(QThread):
    """架构生成工作线程"""

    # 信号定义
    progress = Signal(int, str)  # 进度更新
    completed = Signal(str)  # 完成信号，传递结果
    error = Signal(str)  # 错误信号

    def __init__(self, config: Dict[str, Any], novel_settings: Dict[str, Any], save_path: str):
        """
        初始化工作线程

        Args:
            config: LLM配置
            novel_settings: 小说设定
            save_path: 保存路径
        """
        super().__init__()
        self.config = config
        self.novel_settings = novel_settings
        self.save_path = save_path
        self._is_running = True

    def run(self):
        """在线程中执行架构生成"""
        try:
            self.progress.emit(20, "正在连接LLM服务...")
            logger.info("开始生成小说架构")

            # 获取LLM配置
            llm_configs = self.config.get("llm_configs", {})
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("default", list(llm_configs.keys())[0])
            llm_config = llm_configs[selected_config_name]

            interface_format = llm_config.get('interface_format', 'OpenAI')
            api_key = llm_config.get('api_key', '')
            base_url = llm_config.get('base_url', '')
            model = llm_config.get('model_name', 'gpt-3.5-turbo')
            temperature = llm_config.get('temperature', 0.7)
            max_tokens = llm_config.get('max_tokens', 2048)
            timeout = llm_config.get('timeout', 60)

            # 调用架构生成器
            self.progress.emit(30, "正在生成小说架构...")
            Novel_architecture_generate(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                llm_model=model,
                topic=self.novel_settings['topic'],
                genre=self.novel_settings['genre'],
                number_of_chapters=self.novel_settings['chapter_count'],
                word_number=self.novel_settings['word_count'],
                filepath=self.save_path,
                user_guidance=self.novel_settings.get('worldview', ''),
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            self.progress.emit(90, "正在保存结果...")

            # 读取生成的文件
            architecture_file = os.path.join(self.save_path, "Novel_architecture.txt")
            if os.path.exists(architecture_file):
                with open(architecture_file, 'r', encoding='utf-8') as f:
                    result = f.read()
                self.completed.emit(result)
                self.progress.emit(100, "架构生成完成！")
            else:
                raise FileNotFoundError("生成的文件未找到")

        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)

    def stop(self):
        """停止线程"""
        self._is_running = False
        self.terminate()


class BlueprintGenerationWorker(QThread):
    """章节蓝图生成工作线程"""

    # 信号定义
    progress = Signal(int, str)  # 进度更新
    completed = Signal(str)  # 完成信号，传递结果
    error = Signal(str)  # 错误信号

    def __init__(self, config: Dict[str, Any], save_path: str, number_of_chapters: int, user_guidance: str = ""):
        """
        初始化工作线程

        Args:
            config: LLM配置
            save_path: 保存路径
            number_of_chapters: 章节数量
            user_guidance: 用户指导
        """
        super().__init__()
        self.config = config
        self.save_path = save_path
        self.number_of_chapters = number_of_chapters
        self.user_guidance = user_guidance
        self._is_running = True

    def run(self):
        """在线程中执行章节蓝图生成"""
        try:
            self.progress.emit(20, "正在连接LLM服务...")
            logger.info("开始生成章节蓝图")

            # 获取LLM配置
            llm_configs = self.config.get("llm_configs", {})
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("chapter_outline_llm", list(llm_configs.keys())[0])
            llm_config = llm_configs[selected_config_name]

            interface_format = llm_config.get('interface_format', 'OpenAI')
            api_key = llm_config.get('api_key', '')
            base_url = llm_config.get('base_url', '')
            model = llm_config.get('model_name', 'gpt-3.5-turbo')
            temperature = llm_config.get('temperature', 0.7)
            max_tokens = llm_config.get('max_tokens', 4096)
            timeout = llm_config.get('timeout', 600)

            # 调用章节蓝图生成器
            self.progress.emit(30, "正在生成章节蓝图...")
            Chapter_blueprint_generate(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                llm_model=model,
                filepath=self.save_path,
                number_of_chapters=self.number_of_chapters,
                user_guidance=self.user_guidance,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            self.progress.emit(90, "正在读取生成结果...")

            # 读取生成的文件
            blueprint_file = os.path.join(self.save_path, "Novel_directory.txt")
            if os.path.exists(blueprint_file):
                with open(blueprint_file, 'r', encoding='utf-8') as f:
                    result = f.read()
                self.completed.emit(result)
                self.progress.emit(100, "章节蓝图生成完成！")
            else:
                raise FileNotFoundError("生成的文件未找到")

        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)

    def stop(self):
        """停止线程"""
        self._is_running = False
        self.terminate()


class ChapterGenerationWorker(QThread):
    """章节内容生成工作线程"""

    # 信号定义
    progress = Signal(int, str)  # 进度更新
    completed = Signal(str)  # 完成信号，传递结果
    error = Signal(str)  # 错误信号

    def __init__(self, config: Dict[str, Any], save_path: str, chapter_num: int, word_count: int, user_guidance: str = ""):
        """
        初始化工作线程

        Args:
            config: LLM配置
            save_path: 保存路径
            chapter_num: 章节编号
            word_count: 目标字数
            user_guidance: 用户指导
        """
        super().__init__()
        self.config = config
        self.save_path = save_path
        self.chapter_num = chapter_num
        self.word_count = word_count
        self.user_guidance = user_guidance
        self._is_running = True

    def run(self):
        """在线程中执行章节内容生成"""
        try:
            self.progress.emit(20, "正在连接LLM服务...")
            logger.info(f"开始生成第{self.chapter_num}章内容")

            # 获取LLM配置
            llm_configs = self.config.get("llm_configs", {})
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("prompt_draft_llm", list(llm_configs.keys())[0])
            llm_config = llm_configs[selected_config_name]

            interface_format = llm_config.get('interface_format', 'OpenAI')
            api_key = llm_config.get('api_key', '')
            base_url = llm_config.get('base_url', '')
            model = llm_config.get('model_name', 'gpt-3.5-turbo')
            temperature = llm_config.get('temperature', 0.7)
            max_tokens = llm_config.get('max_tokens', 2048)
            timeout = llm_config.get('timeout', 600)

            # 获取嵌入配置
            embedding_configs = self.config.get("embedding_configs", {})
            selected_embedding_name = list(embedding_configs.keys())[0] if embedding_configs else "OpenAI"
            embedding_config = embedding_configs.get(selected_embedding_name, {})

            embedding_api_key = embedding_config.get('api_key', '')
            embedding_base_url = embedding_config.get('base_url', '')
            embedding_interface_format = embedding_config.get('interface_format', 'openai')
            embedding_model = embedding_config.get('model_name', 'text-embedding-ada-002')
            embedding_retrieval_k = embedding_config.get('retrieval_k', 2)

            # 调用章节生成器
            self.progress.emit(30, f"正在生成第{self.chapter_num}章内容...")
            chapter_content = generate_chapter_draft(
                api_key=api_key,
                base_url=base_url,
                model_name=model,
                filepath=self.save_path,
                novel_number=self.chapter_num,
                word_number=self.word_count,
                temperature=temperature,
                user_guidance=self.user_guidance,
                characters_involved="",  # 可以从蓝图或架构中获取
                key_items="",
                scene_location="",
                time_constraint="",
                embedding_api_key=embedding_api_key,
                embedding_url=embedding_base_url,
                embedding_interface_format=embedding_interface_format,
                embedding_model_name=embedding_model,
                embedding_retrieval_k=embedding_retrieval_k,
                interface_format=interface_format,
                max_tokens=max_tokens,
                timeout=timeout
            )

            self.progress.emit(90, "正在保存结果...")

            # 读取生成的文件
            chapter_file = os.path.join(self.save_path, "chapters", f"chapter_{self.chapter_num}.txt")
            if os.path.exists(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    result = f.read()
                self.completed.emit(result)
                self.progress.emit(100, f"第{self.chapter_num}章生成完成！")
            else:
                raise FileNotFoundError("生成的文件未找到")

        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)

    def stop(self):
        """停止线程"""
        self._is_running = False
        self.terminate()


class BatchChapterGenerationWorker(QThread):
    """批量章节生成工作线程"""

    # 信号定义
    progress = Signal(int, str)  # 进度更新
    chapter_completed = Signal(int, str)  # 单章节完成
    chapter_error = Signal(int, str)  # 单章节错误
    completed = Signal()  # 所有章节完成
    error = Signal(str)  # 总体错误

    def __init__(self, config: Dict[str, Any], save_path: str, start_chapter: int, end_chapter: int, word_count: int):
        """
        初始化批量生成工作线程

        Args:
            config: LLM配置
            save_path: 保存路径
            start_chapter: 起始章节
            end_chapter: 结束章节
            word_count: 目标字数
        """
        super().__init__()
        self.config = config
        self.save_path = save_path
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.word_count = word_count
        self._is_running = True

    def run(self):
        """在线程中执行批量章节生成"""
        try:
            total_chapters = self.end_chapter - self.start_chapter + 1
            completed_chapters = 0

            # 检查是否配置了LLM
            llm_configs = self.config.get("llm_configs", {})
            if not llm_configs:
                raise ValueError("请先在配置管理中设置LLM配置")

            # 获取当前选中的配置
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("default", list(llm_configs.keys())[0])

            if selected_config_name not in llm_configs:
                raise ValueError(f"配置 '{selected_config_name}' 不存在，请检查配置管理")

            # 检查API密钥
            selected_config = llm_configs[selected_config_name]
            if not selected_config.get('api_key'):
                raise ValueError(f"配置 '{selected_config_name}' 缺少API密钥，请检查配置管理")

            # 获取LLM参数
            interface_format = selected_config.get('interface_format', 'OpenAI')
            api_key = selected_config.get('api_key', '')
            base_url = selected_config.get('base_url', '')
            model = selected_config.get('model_name', 'gpt-3.5-turbo')
            temperature = selected_config.get('temperature', 0.7)
            max_tokens = selected_config.get('max_tokens', 2048)
            timeout = selected_config.get('timeout', 600)

            # 获取嵌入配置
            embedding_configs = self.config.get("embedding_configs", {})
            selected_embedding_name = list(embedding_configs.keys())[0] if embedding_configs else "OpenAI"
            embedding_config = embedding_configs.get(selected_embedding_name, {})

            embedding_api_key = embedding_config.get('api_key', '')
            embedding_base_url = embedding_config.get('base_url', '')
            embedding_interface_format = embedding_config.get('interface_format', 'openai')
            embedding_model = embedding_config.get('model_name', 'text-embedding-ada-002')
            embedding_retrieval_k = embedding_config.get('retrieval_k', 2)

            # 逐个生成章节
            for chapter_num in range(self.start_chapter, self.end_chapter + 1):
                if not self._is_running:
                    self.error.emit("用户取消了批量生成")
                    return

                self.progress.emit(
                    int((completed_chapters / total_chapters) * 100),
                    f"正在生成第{chapter_num}章... ({completed_chapters}/{total_chapters})"
                )

                try:
                    from novel_generator.chapter import generate_chapter_draft

                    # 调用章节生成器
                    generate_chapter_draft(
                        api_key=api_key,
                        base_url=base_url,
                        model_name=model,
                        filepath=self.save_path,
                        novel_number=chapter_num,
                        word_number=self.word_count,
                        temperature=temperature,
                        user_guidance="",
                        characters_involved="",
                        key_items="",
                        scene_location="",
                        time_constraint="",
                        embedding_api_key=embedding_api_key,
                        embedding_url=embedding_base_url,
                        embedding_interface_format=embedding_interface_format,
                        embedding_model_name=embedding_model,
                        embedding_retrieval_k=embedding_retrieval_k,
                        interface_format=interface_format,
                        max_tokens=max_tokens,
                        timeout=timeout
                    )

                    # 读取生成的文件
                    chapter_file = os.path.join(self.save_path, "chapters", f"chapter_{chapter_num}.txt")
                    if os.path.exists(chapter_file):
                        with open(chapter_file, 'r', encoding='utf-8') as f:
                            result = f.read()
                        self.chapter_completed.emit(chapter_num, result)
                    else:
                        raise FileNotFoundError(f"第{chapter_num}章生成文件未找到")

                    completed_chapters += 1

                except Exception as e:
                    error_msg = f"第{chapter_num}章生成失败: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.chapter_error.emit(chapter_num, error_msg)

            # 所有章节完成
            self.progress.emit(100, f"批量生成完成！共生成{total_chapters}章")
            self.completed.emit()

        except Exception as e:
            error_msg = f"批量生成失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)

    def stop(self):
        """停止线程"""
        self._is_running = False
        self.terminate()


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
        self.is_batch_generating = False
        self.project_manager = ProjectManager()  # 初始化项目管理器
        self.auto_save_timer = QTimer()  # 自动保存定时器
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # 每30秒自动保存一次
        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)


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

        # 设置工具提示
        self.setup_tooltips()

        # 设置自动保存触发器
        self.setup_auto_save_triggers()

    def setup_tooltips(self):
        """设置工具提示"""
        # 小说基本设定
        if hasattr(self, 'novel_title'):
            tooltip_manager.add_tooltip(self.novel_title, "title")
        if hasattr(self, 'novel_topic'):
            tooltip_manager.add_tooltip(self.novel_topic, "topic")
        if hasattr(self, 'genre'):
            tooltip_manager.add_tooltip(self.genre, "genre")
        if hasattr(self, 'num_chapters'):
            tooltip_manager.add_tooltip(self.num_chapters, "num_chapters")
        if hasattr(self, 'target_words'):
            tooltip_manager.add_tooltip(self.target_words, "word_number")

        # 生成操作按钮
        if hasattr(self, 'generate_architecture_btn'):
            tooltip_manager.add_tooltip(self.generate_architecture_btn, "generate_architecture")
        if hasattr(self, 'generate_blueprint_btn'):
            tooltip_manager.add_tooltip(self.generate_blueprint_btn, "generate_blueprint")
        if hasattr(self, 'generate_chapter_btn'):
            tooltip_manager.add_tooltip(self.generate_chapter_btn, "generate_chapter")
        if hasattr(self, 'consistency_check_btn'):
            tooltip_manager.add_tooltip(self.consistency_check_btn, "consistency_check")

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
        advanced_group = QGroupBox(" 高级设定")
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

        # 项目管理组
        project_group = QGroupBox("📁 项目管理")
        project_layout = QVBoxLayout(project_group)

        # 项目操作按钮
        project_btn_layout = QHBoxLayout()
        self.new_project_btn = QPushButton(" 新建项目")
        self.new_project_btn.clicked.connect(self.create_new_project)
        project_btn_layout.addWidget(self.new_project_btn)

        self.open_project_btn = QPushButton(" 打开项目")
        self.open_project_btn.clicked.connect(self.open_project)
        project_btn_layout.addWidget(self.open_project_btn)
        project_layout.addLayout(project_btn_layout)

        project_btn_layout2 = QHBoxLayout()
        self.save_project_btn = QPushButton(" 保存项目")
        self.save_project_btn.clicked.connect(self.save_current_project)
        self.save_project_btn.setEnabled(False)  # 只有打开项目后才启用
        project_btn_layout2.addWidget(self.save_project_btn)

        self.save_as_btn = QPushButton(" 另存为")
        self.save_as_btn.clicked.connect(self.save_project_as)
        project_btn_layout2.addWidget(self.save_as_btn)
        project_layout.addLayout(project_btn_layout2)

        # 当前项目信息
        self.current_project_label = QLabel("未打开项目")
        self.current_project_label.setStyleSheet("color: gray; font-size: 9pt;")
        project_layout.addWidget(self.current_project_label)

        layout.addWidget(project_group)

        # 保存路径设置
        path_group = QGroupBox(" 保存设置")
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

        self.browse_btn = QPushButton(" 浏览")
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
        info_group = QGroupBox(" 操作说明")
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
        options_group = QGroupBox(" 生成选项")
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
        button_group = QGroupBox(" 开始生成")
        button_layout = QHBoxLayout(button_group)

        self.generate_arch_btn = QPushButton(" 生成小说架构")
        self.generate_arch_btn.clicked.connect(self.generate_architecture)
        self.generate_arch_btn.setStyleSheet("font-weight: bold; padding: 10px; font-size: 11pt;")
        button_layout.addWidget(self.generate_arch_btn)

        layout.addWidget(button_group)

        # 结果显示
        self.arch_result_group = QGroupBox(" 生成结果")
        arch_layout = QVBoxLayout(self.arch_result_group)

        self.arch_result_text = QTextEdit()
        self.arch_result_text.setReadOnly(True)
        self.arch_result_text.setPlaceholderText("架构生成结果将在此显示...")
        arch_layout.addWidget(self.arch_result_text)

        # 结果操作按钮
        result_btn_layout = QHBoxLayout()

        self.save_arch_btn = QPushButton(" 保存架构")
        self.save_arch_btn.clicked.connect(self.save_architecture)
        result_btn_layout.addWidget(self.save_arch_btn)

        self.edit_arch_btn = QPushButton(" 编辑架构")
        self.edit_arch_btn.clicked.connect(self.edit_architecture)
        result_btn_layout.addWidget(self.edit_arch_btn)

        self.export_arch_btn = QPushButton(" 导出架构")
        self.export_arch_btn.clicked.connect(self.export_architecture)
        result_btn_layout.addWidget(self.export_arch_btn)

        result_btn_layout.addStretch()
        arch_layout.addLayout(result_btn_layout)

        layout.addWidget(self.arch_result_group)

        self.operation_tabs.addTab(arch_widget, " 架构生成")

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
        control_group = QGroupBox(" 生成控制")
        control_layout = QFormLayout(control_group)

        control_layout.addRow("起始章节:", self.create_chapter_range_selector())

        self.detail_level = QComboBox()
        self.detail_level.addItems(["简要", "标准", "详细"])
        control_layout.addRow("详细程度:", self.detail_level)

        self.generate_chapter_btn = QPushButton(" 生成章节蓝图")
        self.generate_chapter_btn.clicked.connect(self.generate_chapter_blueprint)
        control_layout.addRow("", self.generate_chapter_btn)

        layout.addWidget(control_group)

        # 章节列表
        list_group = QGroupBox(" 章节列表")
        list_layout = QVBoxLayout(list_group)

        # 这里应该是一个实际的章节列表控件，暂时用TextEdit代替
        self.chapter_list_text = QTextEdit()
        self.chapter_list_text.setReadOnly(True)
        self.chapter_list_text.setPlaceholderText("章节蓝图将在此显示...")
        list_layout.addWidget(self.chapter_list_text)

        layout.addWidget(list_group)

        self.operation_tabs.addTab(blueprint_widget, " 章节规划")

    def create_chapter_generation_tab(self):
        """创建章节生成标签页"""
        chapter_widget = QWidget()
        layout = QVBoxLayout(chapter_widget)
        layout.setSpacing(15)

        # 章节选择
        select_group = QGroupBox(" 章节选择")
        select_layout = QHBoxLayout(select_group)

        select_layout.addWidget(QLabel("选择章节:"))
        self.chapter_selector = QComboBox()
        select_layout.addWidget(self.chapter_selector)

        self.refresh_chapters_btn = QPushButton(" 刷新")
        self.refresh_chapters_btn.clicked.connect(self.refresh_chapter_list)
        select_layout.addWidget(self.refresh_chapters_btn)

        layout.addWidget(select_group)

        # 生成参数
        params_group = QGroupBox(" 生成参数")
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
        generate_group = QGroupBox(" 生成控制")
        generate_layout = QHBoxLayout(generate_group)

        self.generate_single_btn = QPushButton(" 生成当前章节")
        self.generate_single_btn.clicked.connect(self.generate_single_chapter)
        generate_layout.addWidget(self.generate_single_btn)

        self.generate_batch_btn = QPushButton(" 批量生成")
        self.generate_batch_btn.setToolTip("从第1章开始生成到当前选中的章节")
        self.generate_batch_btn.clicked.connect(self.generate_batch_chapters)
        generate_layout.addWidget(self.generate_batch_btn)

        self.cancel_batch_btn = QPushButton(" 取消生成")
        self.cancel_batch_btn.setEnabled(False)
        self.cancel_batch_btn.clicked.connect(self.cancel_batch_generation)
        self.cancel_batch_btn.setToolTip("取消当前正在进行的批量生成")
        generate_layout.addWidget(self.cancel_batch_btn)

        layout.addWidget(generate_group)

        # 内容预览
        preview_group = QGroupBox(" 内容预览")
        preview_layout = QVBoxLayout(preview_group)

        self.chapter_preview = QTextEdit()
        self.chapter_preview.setReadOnly(True)
        self.chapter_preview.setPlaceholderText("章节内容将在此显示...")
        preview_layout.addWidget(self.chapter_preview)

        layout.addWidget(preview_group)

        self.operation_tabs.addTab(chapter_widget, " 章节生成")

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

        self.import_knowledge_btn = QPushButton(" 导入知识库")
        self.import_knowledge_btn.clicked.connect(self.import_knowledge)
        import_layout.addRow("", self.import_knowledge_btn)

        layout.addWidget(import_group)

        # 一致性检查
        consistency_group = QGroupBox(" 一致性检查")
        consistency_layout = QVBoxLayout(consistency_group)

        self.check_consistency_btn = QPushButton(" 执行一致性检查")
        self.check_consistency_btn.clicked.connect(self.check_consistency)
        consistency_layout.addWidget(self.check_consistency_btn)

        layout.addWidget(consistency_group)

        # 内容优化
        optimize_group = QGroupBox(" 内容优化")
        optimize_layout = QVBoxLayout(optimize_group)

        self.optimize_content_btn = QPushButton(" 优化选定内容")
        self.optimize_content_btn.clicked.connect(self.optimize_content)
        optimize_layout.addWidget(self.optimize_content_btn)

        layout.addWidget(optimize_group)

        # 数据导出
        export_group = QGroupBox(" 数据导出")
        export_layout = QFormLayout(export_group)

        self.export_format = QComboBox()
        self.export_format.addItems(["Word文档", "PDF", "TXT", "Markdown"])
        export_layout.addRow("导出格式:", self.export_format)

        self.export_data_btn = QPushButton(" 导出小说")
        self.export_data_btn.clicked.connect(self.export_novel)
        export_layout.addRow("", self.export_data_btn)

        layout.addWidget(export_group)
        layout.addStretch()

        self.operation_tabs.addTab(batch_widget, " 批量操作")

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

        browse_btn = QPushButton(" 浏览")
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
        log_group = QGroupBox(" 操作日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 9pt;")
        self.log_text.setPlaceholderText("操作日志将在此显示...")
        log_layout.addWidget(self.log_text)

        # 日志控制按钮
        log_control_layout = QHBoxLayout()

        self.clear_log_btn = QPushButton(" 清空日志")
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
        try:
            novel_title = self.novel_title.text().strip()
            novel_topic = self.novel_topic.toPlainText().strip()

            validate_required(novel_title, "小说标题")
            validate_required(novel_topic, "主题描述")

            # 检查是否配置了LLM
            llm_configs = self.config.get("llm_configs", {})
            if not llm_configs:
                show_error_dialog(self, "配置错误", "请先在配置管理中设置LLM配置")
                return

            # 获取当前选中的配置
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("default", list(llm_configs.keys())[0])

            if selected_config_name not in llm_configs:
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 不存在，请检查配置管理")
                return

            # 检查API密钥
            selected_config = llm_configs[selected_config_name]
            if not selected_config.get('api_key'):
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 缺少API密钥，请检查配置管理")
                return

            # 检查保存路径
            save_path = self.save_path.text().strip()
            if not save_path:
                show_error_dialog(self, "验证失败", "请选择保存路径")
                return

        except ValueError as e:
            show_error_dialog(self, "验证失败", str(e))
            return

        # 准备参数
        novel_settings = {
            'title': novel_title,
            'topic': novel_topic,
            'genre': self.novel_genre.currentText(),
            'chapter_count': self.chapter_count.value(),
            'word_count': self.word_count.value(),
            'worldview': self.worldview_text.toPlainText().strip(),
            'writing_style': self.writing_style.currentText(),
            'target_readers': self.target_readers.currentText()
        }

        # 创建并启动工作线程
        self.worker = ArchitectureGenerationWorker(
            config=self.config,
            novel_settings=novel_settings,
            save_path=save_path
        )

        # 连接信号
        self.worker.progress.connect(self.update_progress)
        self.worker.completed.connect(self.on_architecture_completed)
        self.worker.error.connect(self.on_architecture_error)

        # 更新UI状态
        self.is_generating = True
        self.generation_started.emit()
        self.generate_arch_btn.setEnabled(False)
        self.log_message("开始生成小说架构...")
        self.update_progress(10, "准备中...")

        # 启动线程
        self.worker.start()
        self.log_message("架构生成任务已启动")

    def on_architecture_completed(self, result: str):
        """架构生成完成"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_arch_btn.setEnabled(True)

        # 显示结果
        self.arch_result_text.setPlainText(result)
        self.log_message("架构生成完成！")
        self.update_progress(100, "架构生成完成")

        # 更新项目状态
        if self.project_manager.get_current_project():
            self.project_manager.update_generation_status(0, is_completed=False)  # 架构不算章节
            self.log_message("项目状态已更新")

        show_info_dialog(self, "成功", "小说架构生成完成！")

    def on_architecture_error(self, error_msg: str):
        """架构生成错误"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_arch_btn.setEnabled(True)

        self.log_message(f"架构生成失败: {error_msg}")
        self.update_progress(0, "生成失败")
        show_error_dialog(self, "生成失败", error_msg)

    def on_blueprint_completed(self, result: str):
        """章节蓝图生成完成"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_chapter_btn.setEnabled(True)

        # 显示结果
        self.chapter_list_text.setPlainText(result)
        self.log_message("章节蓝图生成完成！")
        self.update_progress(100, "章节蓝图生成完成")

        # 更新项目状态
        if self.project_manager.get_current_project():
            self.project_manager.update_generation_status(0, is_completed=False)  # 蓝图不算章节
            self.log_message("项目状态已更新")

        show_info_dialog(self, "成功", "章节蓝图生成完成！")

    def on_blueprint_error(self, error_msg: str):
        """章节蓝图生成错误"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_chapter_btn.setEnabled(True)

        self.log_message(f"章节蓝图生成失败: {error_msg}")
        self.update_progress(0, "生成失败")
        show_error_dialog(self, "生成失败", error_msg)

    def on_chapter_completed(self, result: str):
        """章节生成完成"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_single_btn.setEnabled(True)

        # 显示结果
        self.chapter_preview.setPlainText(result)
        self.log_message("章节内容生成完成！")
        self.update_progress(100, "章节生成完成")

        # 更新项目状态
        if self.project_manager.get_current_project():
            # 提取当前章节号
            current_text = self.chapter_selector.currentText()
            if current_text:
                import re
                match = re.search(r'第(\d+)章', current_text)
                if match:
                    chapter_num = int(match.group(1))
                    self.project_manager.update_generation_status(chapter_num)
                    self.log_message("项目状态已更新")

        show_info_dialog(self, "成功", "章节内容生成完成！")

    def on_chapter_error(self, error_msg: str):
        """章节生成错误"""
        self.is_generating = False
        self.generation_finished.emit()
        self.generate_single_btn.setEnabled(True)

        self.log_message(f"章节生成失败: {error_msg}")
        self.update_progress(0, "生成失败")
        show_error_dialog(self, "生成失败", error_msg)

    def complete_architecture_generation(self):
        """完成架构生成 - 已弃用，使用on_architecture_completed代替"""
        pass

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
        self.edit_arch_btn.setText(" 保存编辑")
        self.edit_arch_btn.clicked.disconnect()
        self.edit_arch_btn.clicked.connect(self.save_architecture_edits)

    def save_architecture_edits(self):
        """保存架构编辑"""
        self.arch_result_text.setReadOnly(True)
        self.edit_arch_btn.setText(" 编辑架构")
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
        if self.is_generating:
            show_error_dialog(self, "错误", "正在生成中，请等待完成")
            return

        # 验证输入
        try:
            # 检查是否配置了LLM
            llm_configs = self.config.get("llm_configs", {})
            if not llm_configs:
                show_error_dialog(self, "配置错误", "请先在配置管理中设置LLM配置")
                return

            # 获取当前选中的配置
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("default", list(llm_configs.keys())[0])

            if selected_config_name not in llm_configs:
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 不存在，请检查配置管理")
                return

            # 检查API密钥
            selected_config = llm_configs[selected_config_name]
            if not selected_config.get('api_key'):
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 缺少API密钥，请检查配置管理")
                return

            # 检查保存路径
            save_path = self.save_path.text().strip()
            if not save_path:
                show_error_dialog(self, "验证失败", "请选择保存路径")
                return

            # 检查架构文件是否存在
            architecture_file = os.path.join(save_path, "Novel_architecture.txt")
            if not os.path.exists(architecture_file):
                show_error_dialog(self, "验证失败", "请先生成小说架构")
                return

        except ValueError as e:
            show_error_dialog(self, "验证失败", str(e))
            return

        # 创建并启动工作线程
        self.worker = BlueprintGenerationWorker(
            config=self.config,
            save_path=save_path,
            number_of_chapters=self.chapter_count.value(),
            user_guidance=""  # 可以从UI获取
        )

        # 连接信号
        self.worker.progress.connect(self.update_progress)
        self.worker.completed.connect(self.on_blueprint_completed)
        self.worker.error.connect(self.on_blueprint_error)

        # 更新UI状态
        self.is_generating = True
        self.generation_started.emit()
        self.generate_chapter_btn.setEnabled(False)
        self.log_message("开始生成章节蓝图...")
        self.update_progress(10, "准备中...")

        # 启动线程
        self.worker.start()
        self.log_message("章节蓝图生成任务已启动")

    def refresh_chapter_list(self):
        """刷新章节列表"""
        self.chapter_selector.clear()
        for i in range(1, self.chapter_count.value() + 1):
            self.chapter_selector.addItem(f"第{i}章")
        self.log_message("章节列表已刷新")

    def generate_single_chapter(self):
        """生成单个章节"""
        if self.is_generating:
            show_error_dialog(self, "错误", "正在生成中，请等待完成")
            return

        # 验证输入
        try:
            # 获取选中的章节
            current_text = self.chapter_selector.currentText()
            if not current_text:
                show_error_dialog(self, "错误", "请选择章节")
                return

            # 从文本中提取章节号
            import re
            match = re.search(r'第(\d+)章', current_text)
            if not match:
                show_error_dialog(self, "错误", "无法解析章节号")
                return

            chapter_num = int(match.group(1))

            # 检查是否配置了LLM
            llm_configs = self.config.get("llm_configs", {})
            if not llm_configs:
                show_error_dialog(self, "配置错误", "请先在配置管理中设置LLM配置")
                return

            # 获取当前选中的配置
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("default", list(llm_configs.keys())[0])

            if selected_config_name not in llm_configs:
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 不存在，请检查配置管理")
                return

            # 检查API密钥
            selected_config = llm_configs[selected_config_name]
            if not selected_config.get('api_key'):
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 缺少API密钥，请检查配置管理")
                return

            # 检查保存路径
            save_path = self.save_path.text().strip()
            if not save_path:
                show_error_dialog(self, "验证失败", "请选择保存路径")
                return

            # 检查蓝图文件是否存在
            blueprint_file = os.path.join(save_path, "Novel_directory.txt")
            if not os.path.exists(blueprint_file):
                show_error_dialog(self, "验证失败", "请先生成章节蓝图")
                return

            # 获取目标字数
            word_count = self.chapter_word_target.value()

        except ValueError as e:
            show_error_dialog(self, "验证失败", str(e))
            return

        # 创建并启动工作线程
        self.worker = ChapterGenerationWorker(
            config=self.config,
            save_path=save_path,
            chapter_num=chapter_num,
            word_count=word_count,
            user_guidance=""  # 可以从UI获取用户指导
        )

        # 连接信号
        self.worker.progress.connect(self.update_progress)
        self.worker.completed.connect(self.on_chapter_completed)
        self.worker.error.connect(self.on_chapter_error)

        # 更新UI状态
        self.is_generating = True
        self.generation_started.emit()
        self.generate_single_btn.setEnabled(False)
        self.log_message(f"开始生成第{chapter_num}章...")
        self.update_progress(10, "准备中...")

        # 启动线程
        self.worker.start()
        self.log_message(f"第{chapter_num}章生成任务已启动")

    def generate_batch_chapters(self):
        """批量生成章节"""
        if self.is_generating or self.is_batch_generating:
            show_error_dialog(self, "错误", "正在生成中，请等待完成")
            return

        # 验证输入
        try:
            # 检查是否配置了LLM
            llm_configs = self.config.get("llm_configs", {})
            if not llm_configs:
                show_error_dialog(self, "配置错误", "请先在配置管理中设置LLM配置")
                return

            # 获取当前选中的配置
            choose_configs = self.config.get("choose_configs", {})
            selected_config_name = choose_configs.get("default", list(llm_configs.keys())[0])

            if selected_config_name not in llm_configs:
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 不存在，请检查配置管理")
                return

            # 检查API密钥
            selected_config = llm_configs[selected_config_name]
            if not selected_config.get('api_key'):
                show_error_dialog(self, "配置错误", f"配置 '{selected_config_name}' 缺少API密钥，请检查配置管理")
                return

            # 检查保存路径
            save_path = self.save_path.text().strip()
            if not save_path:
                show_error_dialog(self, "验证失败", "请选择保存路径")
                return

            # 检查蓝图文件是否存在
            blueprint_file = os.path.join(save_path, "Novel_directory.txt")
            if not os.path.exists(blueprint_file):
                show_error_dialog(self, "验证失败", "请先生成章节蓝图")
                return

            # 获取章节范围
            current_text = self.chapter_selector.currentText()
            if not current_text:
                show_error_dialog(self, "错误", "请选择章节")
                return

            import re
            match = re.search(r'第(\d+)章', current_text)
            if not match:
                show_error_dialog(self, "错误", "无法解析章节号")
                return

            selected_chapter = int(match.group(1))

            # 批量生成范围：从第1章到选中的章节
            start_chapter = 1
            end_chapter = selected_chapter

            # 获取目标字数
            word_count = self.chapter_word_target.value()

        except ValueError as e:
            show_error_dialog(self, "验证失败", str(e))
            return

        # 创建并启动工作线程
        self.batch_worker = BatchChapterGenerationWorker(
            config=self.config,
            save_path=save_path,
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            word_count=word_count
        )

        # 连接信号
        self.batch_worker.progress.connect(self.update_batch_progress)
        self.batch_worker.chapter_completed.connect(self.on_batch_chapter_completed)
        self.batch_worker.chapter_error.connect(self.on_batch_chapter_error)
        self.batch_worker.completed.connect(self.on_batch_completed)
        self.batch_worker.error.connect(self.on_batch_error)

        # 更新UI状态
        self.is_batch_generating = True
        self.generation_started.emit()
        self.generate_batch_btn.setEnabled(False)
        self.generate_single_btn.setEnabled(False)
        self.cancel_batch_btn.setEnabled(True)
        self.log_message(f"开始批量生成第{start_chapter}章到第{end_chapter}章...")
        self.update_progress(0, "准备批量生成...")

        # 启动线程
        self.batch_worker.start()
        self.log_message(f"批量生成任务已启动，共需生成{end_chapter - start_chapter + 1}章")

    def cancel_batch_generation(self):
        """取消批量生成"""
        if hasattr(self, 'batch_worker') and self.batch_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认取消",
                "确定要取消当前的批量生成吗？已完成的章节将保留。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.log_message("用户取消了批量生成")
                self.batch_worker.stop()
                # 等待线程结束
                self.batch_worker.wait(3000)  # 等待3秒
                self.on_batch_error("用户取消了生成")

    def update_batch_progress(self, value: int, message: str):
        """更新批量生成进度"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.log_message(message)

    def on_batch_chapter_completed(self, chapter_num: int, result: str):
        """批量生成中单个章节完成"""
        self.log_message(f"第{chapter_num}章生成完成")
        # 可以选择将结果添加到预览中
        self.chapter_preview.setPlainText(result)

        # 更新项目状态
        if self.project_manager.get_current_project():
            self.project_manager.update_generation_status(chapter_num)
            self.log_message(f"第{chapter_num}章状态已更新到项目")

    def on_batch_chapter_error(self, chapter_num: int, error_msg: str):
        """批量生成中单个章节错误"""
        self.log_message(f"第{chapter_num}章生成失败: {error_msg}")
        show_error_dialog(self, f"第{chapter_num}章生成失败", error_msg)

    def on_batch_completed(self):
        """批量生成完成"""
        self.is_batch_generating = False
        self.generation_finished.emit()
        self.generate_batch_btn.setEnabled(True)
        self.generate_single_btn.setEnabled(True)
        self.cancel_batch_btn.setEnabled(False)

        self.log_message("批量生成完成！")
        self.update_progress(100, "批量生成完成")
        show_info_dialog(self, "成功", "批量章节生成完成！")

    def on_batch_error(self, error_msg: str):
        """批量生成错误"""
        self.is_batch_generating = False
        self.generation_finished.emit()
        self.generate_batch_btn.setEnabled(True)
        self.generate_single_btn.setEnabled(True)
        self.cancel_batch_btn.setEnabled(False)

        # 如果是用户主动取消，不显示错误对话框
        if error_msg == "用户取消了生成":
            self.log_message("批量生成已取消")
            self.update_progress(0, "已取消")
        else:
            self.log_message(f"批量生成失败: {error_msg}")
            self.update_progress(0, "生成失败")
            show_error_dialog(self, "生成失败", error_msg)

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

    # ==================== 项目管理功能 ====================

    def create_new_project(self):
        """创建新项目"""
        from PySide6.QtWidgets import QFileDialog, QInputDialog

        # 弹出输入对话框获取项目名称
        project_name, ok = QInputDialog.getText(
            self, "新建项目", "请输入项目名称:"
        )
        if not ok or not project_name.strip():
            return

        # 选择项目保存路径
        project_path = QFileDialog.getExistingDirectory(
            self, "选择项目保存位置", ""
        )
        if not project_path:
            return

        # 构建完整的项目路径
        full_path = os.path.join(project_path, project_name.strip())

        # 准备项目信息
        project_info = {
            "name": project_name.strip(),
            "title": self.novel_title.text().strip(),
            "topic": self.novel_topic.toPlainText().strip(),
            "genre": self.novel_genre.currentText(),
            "chapter_count": self.chapter_count.value(),
            "word_count": self.word_count.value(),
            "worldview": self.worldview_text.toPlainText().strip(),
            "writing_style": self.writing_style.currentText(),
            "target_readers": self.target_readers.currentText()
        }

        # 创建项目
        if self.project_manager.create_project(full_path, project_info):
            # 更新UI
            self.save_path.setText(full_path)
            self.current_project_label.setText(f"当前项目: {project_name}")
            self.current_project_label.setStyleSheet("color: green; font-size: 9pt;")
            self.save_project_btn.setEnabled(True)

            self.log_message(f"项目创建成功: {full_path}")
            show_info_dialog(self, "成功", "项目创建成功！")
        else:
            show_error_dialog(self, "错误", "项目创建失败！")

    def open_project(self):
        """打开项目"""
        from PySide6.QtWidgets import QFileDialog

        # 选择项目文件夹
        project_path = QFileDialog.getExistingDirectory(
            self, "选择要打开的项目", ""
        )
        if not project_path:
            return

        # 验证是否为有效项目
        if not self.project_manager.is_valid_project(project_path):
            show_error_dialog(self, "错误", "所选文件夹不是有效的项目！")
            return

        # 加载项目
        project_data = self.project_manager.load_project(project_path)
        if project_data is None:
            show_error_dialog(self, "错误", "项目加载失败！")
            return

        # 恢复UI设置
        self._restore_ui_from_project_data(project_data)

        # 更新UI
        self.save_path.setText(project_path)
        project_name = project_data.get("project_info", {}).get("name", "未命名")
        self.current_project_label.setText(f"当前项目: {project_name}")
        self.current_project_label.setStyleSheet("color: green; font-size: 9pt;")
        self.save_project_btn.setEnabled(True)

        self.log_message(f"项目加载成功: {project_path}")
        show_info_dialog(self, "成功", "项目加载成功！")

    def save_current_project(self):
        """保存当前项目"""
        # 获取当前UI数据
        project_data = self._collect_ui_data()

        # 获取项目路径
        project_path = self.save_path.text().strip()
        if not project_path:
            show_error_dialog(self, "错误", "请先选择保存路径！")
            return

        # 检查是否有打开的项目
        if not self.project_manager.get_current_project():
            # 如果没有打开项目，先创建一个
            project_name = self.novel_title.text().strip() or "未命名项目"
            project_info = {
                "name": project_name,
                "title": self.novel_title.text().strip(),
                "topic": self.novel_topic.toPlainText().strip(),
                "genre": self.novel_genre.currentText(),
                "chapter_count": self.chapter_count.value(),
                "word_count": self.word_count.value(),
                "worldview": self.worldview_text.toPlainText().strip(),
                "writing_style": self.writing_style.currentText(),
                "target_readers": self.target_readers.currentText()
            }
            if not self.project_manager.create_project(project_path, project_info):
                show_error_dialog(self, "错误", "项目创建失败！")
                return

        # 保存项目
        if self.project_manager.save_project(project_path, project_data):
            self.log_message("项目已保存")
            show_info_dialog(self, "成功", "项目保存成功！")
        else:
            show_error_dialog(self, "错误", "项目保存失败！")

    def save_project_as(self):
        """另存为项目"""
        from PySide6.QtWidgets import QFileDialog, QInputDialog

        # 获取新项目名称
        project_name, ok = QInputDialog.getText(
            self, "另存为", "请输入新项目名称:", text=self.novel_title.text().strip()
        )
        if not ok or not project_name.strip():
            return

        # 选择新保存路径
        new_path = QFileDialog.getExistingDirectory(
            self, "选择新项目保存位置", ""
        )
        if not new_path:
            return

        # 构建完整路径
        full_path = os.path.join(new_path, project_name.strip())

        # 准备项目数据
        project_data = self._collect_ui_data()
        project_data["project_info"]["name"] = project_name.strip()

        # 创建并保存新项目
        if self.project_manager.create_project(full_path, project_data):
            if self.project_manager.save_project(full_path, project_data):
                # 更新UI
                self.save_path.setText(full_path)
                self.current_project_label.setText(f"当前项目: {project_name}")
                self.current_project_label.setStyleSheet("color: green; font-size: 9pt;")
                self.save_project_btn.setEnabled(True)

                self.log_message(f"项目另存为成功: {full_path}")
                show_info_dialog(self, "成功", "项目另存为成功！")
            else:
                show_error_dialog(self, "错误", "项目保存失败！")
        else:
            show_error_dialog(self, "错误", "项目创建失败！")

    def _collect_ui_data(self) -> Dict[str, Any]:
        """收集当前UI数据为项目数据"""
        return {
            "project_info": {
                "name": self.novel_title.text().strip() or "未命名项目",
                "title": self.novel_title.text().strip(),
                "topic": self.novel_topic.toPlainText().strip(),
                "genre": self.novel_genre.currentText(),
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0"
            },
            "settings": {
                "chapter_count": self.chapter_count.value(),
                "word_count": self.word_count.value(),
                "worldview": self.worldview_text.toPlainText().strip(),
                "writing_style": self.writing_style.currentText(),
                "target_readers": self.target_readers.currentText(),
                "save_path": self.save_path.text().strip()
            },
            "generation_status": {
                "architecture_generated": os.path.exists(os.path.join(self.save_path.text(), "Novel_architecture.txt")),
                "blueprint_generated": os.path.exists(os.path.join(self.save_path.text(), "Novel_directory.txt")),
                "generated_chapters": self._get_generated_chapters(),
                "total_words": self._calculate_total_words(),
                "last_chapter": max(self._get_generated_chapters()) if self._get_generated_chapters() else 0
            },
            "files": {
                "architecture_file": "Novel_architecture.txt",
                "blueprint_file": "Novel_directory.txt",
                "summary_file": "global_summary.txt",
                "character_state_file": "character_state.txt",
                "chapters_dir": "chapters"
            },
            "ui_state": {
                "selected_chapter": self.chapter_selector.currentIndex() + 1 if self.chapter_selector.currentText() else 1,
                "active_tab": self.operation_tabs.currentIndex()
            }
        }

    def _restore_ui_from_project_data(self, project_data: Dict[str, Any]):
        """从项目数据恢复UI设置"""
        try:
            settings = project_data.get("settings", {})
            project_info = project_data.get("project_info", {})

            # 恢复基本设置
            self.novel_title.setText(project_info.get("title", ""))
            self.novel_topic.setText(project_info.get("topic", ""))
            self.novel_genre.setCurrentText(project_info.get("genre", "玄幻"))
            self.chapter_count.setValue(settings.get("chapter_count", 20))
            self.word_count.setValue(settings.get("word_count", 3000))
            self.worldview_text.setText(settings.get("worldview", ""))
            self.writing_style.setCurrentText(settings.get("writing_style", "简洁明快"))
            self.target_readers.setCurrentText(settings.get("target_readers", "全年龄"))

            # 刷新章节列表
            self.refresh_chapter_list()

            # 恢复UI状态
            ui_state = project_data.get("ui_state", {})
            if "active_tab" in ui_state:
                self.operation_tabs.setCurrentIndex(ui_state["active_tab"])

        except Exception as e:
            logger.error(f"恢复UI设置失败: {str(e)}")
            self.log_message(f"恢复UI设置失败: {str(e)}")

    def _get_generated_chapters(self) -> List[int]:
        """获取已生成的章节列表"""
        chapters = []
        save_path = self.save_path.text().strip()
        if not save_path:
            return chapters

        chapters_dir = os.path.join(save_path, "chapters")
        if not os.path.exists(chapters_dir):
            return chapters

        try:
            for filename in os.listdir(chapters_dir):
                if filename.startswith("chapter_") and filename.endswith(".txt"):
                    # 提取章节号
                    chapter_num = filename.replace("chapter_", "").replace(".txt", "")
                    if chapter_num.isdigit():
                        chapters.append(int(chapter_num))
            chapters.sort()
        except Exception as e:
            logger.error(f"获取已生成章节列表失败: {str(e)}")

        return chapters

    def _calculate_total_words(self) -> int:
        """计算总字数"""
        save_path = self.save_path.text().strip()
        if not save_path:
            return 0

        chapters_dir = os.path.join(save_path, "chapters")
        if not os.path.exists(chapters_dir):
            return 0

        total_words = 0
        try:
            for filename in os.listdir(chapters_dir):
                if filename.startswith("chapter_") and filename.endswith(".txt"):
                    chapter_path = os.path.join(chapters_dir, filename)
                    content = read_file(chapter_path)
                    total_words += len(content)
        except Exception as e:
            logger.error(f"计算总字数失败: {str(e)}")

        return total_words

    def auto_save(self):
        """自动保存当前项目"""
        # 只有在有打开的项目时才自动保存
        if not self.project_manager.get_current_project():
            return

        # 只有在有保存路径时才自动保存
        if not self.save_path.text().strip():
            return

        try:
            # 收集当前数据
            project_data = self._collect_ui_data()

            # 保存项目
            self.project_manager.save_project(self.save_path.text().strip(), project_data)
            # 注意：不显示对话框，只记录日志
            self.log_message("自动保存完成")
        except Exception as e:
            logger.error(f"自动保存失败: {str(e)}")
            # 自动保存失败不显示错误对话框，避免干扰用户

    def setup_auto_save_triggers(self):
        """设置自动保存的触发器"""
        # 当重要设置改变时，触发自动保存
        self.novel_title.textChanged.connect(self.trigger_auto_save)
        self.novel_topic.textChanged.connect(self.trigger_auto_save)
        self.chapter_count.valueChanged.connect(self.trigger_auto_save)
        self.word_count.valueChanged.connect(self.trigger_auto_save)
        self.save_path.textChanged.connect(self.trigger_auto_save)

    def trigger_auto_save(self):
        """触发自动保存（延迟执行）"""
        # 重置定时器，避免频繁保存
        self.auto_save_timer.stop()
        self.auto_save_timer.start(5000)  # 5秒后执行自动保存

    def closeEvent(self, event):
        """窗口关闭事件，自动保存"""
        if self.project_manager.get_current_project():
            self.auto_save()
        event.accept()
