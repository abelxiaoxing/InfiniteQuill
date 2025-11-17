# ui_qt/coherence_check_thread.py
# -*- coding: utf-8 -*-
"""
连贯性检查后台线程
在后台执行连贯性检查，避免阻塞UI
"""

import logging
from PySide6.QtCore import QThread, Signal

from novel_generator.coherence_checker import CoherenceChecker


class CoherenceCheckThread(QThread):
    """连贯性检查后台线程"""

    # 信号定义
    progress_updated = Signal(str)  # 进度更新消息
    check_completed = Signal(object, list, str)  # 检查完成 (scores, issues, report_text)
    check_failed = Signal(str)  # 检查失败

    def __init__(self, project_path: str, chapters: list, llm_config: dict):
        super().__init__()
        self.project_path = project_path
        self.chapters = chapters
        self.llm_config = llm_config
        self.logger = logging.getLogger(__name__)

    def run(self):
        """执行连贯性检查"""
        try:
            self.progress_updated.emit("正在初始化连贯性检查器...")

            # 创建连贯性检查器
            checker = CoherenceChecker(self.llm_config, self.project_path)

            self.progress_updated.emit(f"正在分析 {len(self.chapters)} 个章节...")

            # 执行连贯性检查
            scores, issues, report_text = checker.run_coherence_check(self.chapters)

            self.progress_updated.emit("正在生成检查报告...")

            # 发出完成信号
            self.check_completed.emit(scores, issues, report_text)

        except Exception as e:
            error_message = f"连贯性检查失败: {str(e)}"
            self.logger.error(error_message)
            self.check_failed.emit(error_message)