# ui_qt/dialogs/progress_dialog.py
# -*- coding: utf-8 -*-
"""
进度对话框
显示长时间运行任务的进度
"""

from typing import Optional, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QTextEdit, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont


class ProgressDialog(QDialog):
    """进度对话框"""

    # 信号定义
    cancelled = Signal()

    def __init__(self, title: str = "处理中", parent=None):
        super().__init__(parent)
        self.title = title
        self.is_cancelled = False
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.resize(500, 300)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # 状态信息
        self.status_label = QLabel("正在处理...")
        self.status_label.setStyleSheet("color: #666; margin: 5px 0;")
        layout.addWidget(self.status_label)

        # 详细信息（可选）
        self.details_group = QGroupBox("详细信息")
        self.details_layout = QVBoxLayout(self.details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        self.details_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 9pt;")
        self.details_layout.addWidget(self.details_text)

        self.details_group.hide()  # 默认隐藏
        layout.addWidget(self.details_group)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.show_details_btn = QPushButton("📋 显示详情")
        self.show_details_btn.setCheckable(True)
        self.show_details_btn.clicked.connect(self.toggle_details)
        button_layout.addWidget(self.show_details_btn)

        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def set_progress(self, value: int, status: str = ""):
        """设置进度"""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)

    def set_range(self, minimum: int, maximum: int):
        """设置进度范围"""
        self.progress_bar.setRange(minimum, maximum)

    def add_detail(self, message: str):
        """添加详细信息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.details_text.append(f"[{timestamp}] {message}")

        # 自动滚动到底部
        scrollbar = self.details_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def toggle_details(self, show: bool):
        """切换详细信息显示"""
        if show:
            self.details_group.show()
            self.show_details_btn.setText("📋 隐藏详情")
            self.adjustSize()
        else:
            self.details_group.hide()
            self.show_details_btn.setText("📋 显示详情")
            self.adjustSize()

    def cancel(self):
        """取消操作"""
        reply = self.question_dialog("确认取消", "确定要取消当前操作吗？")
        if reply:
            self.is_cancelled = True
            self.cancelled.emit()
            self.reject()

    def question_dialog(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def isCancelled(self) -> bool:
        """检查是否已取消"""
        return self.is_cancelled

    def reset(self):
        """重置对话框"""
        self.progress_bar.setValue(0)
        self.status_label.setText("正在处理...")
        self.details_text.clear()
        self.is_cancelled = False


class TaskProgressDialog(ProgressDialog):
    """任务进度对话框 - 带有异步任务支持"""

    def __init__(self, task_func: Callable, title: str = "处理中", parent=None):
        super().__init__(title, parent)
        self.task_func = task_func
        self.task_result = None
        self.task_error = None
        self.setup_task_timer()

    def setup_task_timer(self):
        """设置任务定时器"""
        self.task_timer = QTimer()
        self.task_timer.timeout.connect(self.execute_task)
        self.task_timer.setSingleShot(True)

    def start_task(self):
        """开始任务"""
        self.reset()
        self.show()
        # 使用单次定时器延迟执行任务，确保界面先显示
        self.task_timer.start(10)

    def execute_task(self):
        """执行任务"""
        try:
            # 执行任务并获取结果
            if callable(self.task_func):
                self.add_detail("开始执行任务...")
                self.task_result = self.task_func(self)
                self.add_detail("任务执行完成")
                self.set_progress(100, "完成")

                # 延迟关闭对话框
                QTimer.singleShot(1000, self.accept)
            else:
                raise ValueError("任务必须是可调用对象")
        except Exception as e:
            self.task_error = str(e)
            self.add_detail(f"任务执行失败: {e}")
            self.set_progress(0, f"失败: {e}")

            # 显示错误消息
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"任务执行失败:\n{str(e)}")

    def get_result(self):
        """获取任务结果"""
        return self.task_result

    def get_error(self):
        """获取错误信息"""
        return self.task_error


class MultiStepProgressDialog(ProgressDialog):
    """多步骤进度对话框"""

    def __init__(self, steps: list, title: str = "处理中", parent=None):
        super().__init__(title, parent)
        self.steps = steps
        self.current_step = 0
        self.total_steps = len(steps)
        self.setup_steps()

    def setup_steps(self):
        """设置步骤"""
        self.set_range(0, self.total_steps * 100)
        self.update_current_step()

    def update_current_step(self):
        """更新当前步骤"""
        if self.current_step < len(self.steps):
            step_name = self.steps[self.current_step]
            overall_progress = self.current_step * 100
            self.set_progress(overall_progress, f"步骤 {self.current_step + 1}/{self.total_steps}: {step_name}")
            self.add_detail(f"开始步骤 {self.current_step + 1}: {step_name}")

    def next_step(self, step_progress: int = 100):
        """进入下一步"""
        if self.current_step < self.total_steps:
            overall_progress = self.current_step * 100 + step_progress
            self.set_progress(overall_progress, f"步骤 {self.current_step + 1}/{self.total_steps}: {self.steps[self.current_step]}")

            if step_progress >= 100:
                self.add_detail(f"完成步骤 {self.current_step + 1}: {self.steps[self.current_step]}")
                self.current_step += 1
                if self.current_step < self.total_steps:
                    QTimer.singleShot(100, self.update_current_step)

    def set_step_progress(self, progress: int):
        """设置当前步骤进度"""
        overall_progress = self.current_step * 100 + progress
        step_name = self.steps[self.current_step] if self.current_step < len(self.steps) else ""
        self.set_progress(overall_progress, f"步骤 {self.current_step + 1}/{self.total_steps}: {step_name} ({progress}%)")