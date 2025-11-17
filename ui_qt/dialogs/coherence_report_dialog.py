# ui_qt/dialogs/coherence_report_dialog.py
# -*- coding: utf-8 -*-
"""
连贯性检查报告对话框
显示跨章节连贯性检查的结果和建议
"""

import os
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QSplitter,
    QFrame, QScrollArea, QGroupBox, QProgressBar, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor, QIcon

from novel_generator.coherence_checker import CoherenceIssue, CoherenceScore


class CoherenceReportDialog(QDialog):
    """连贯性检查报告对话框"""

    def __init__(self, scores: CoherenceScore, issues: List[CoherenceIssue],
                 report_text: str, parent=None):
        super().__init__(parent)
        self.scores = scores
        self.issues = issues
        self.report_text = report_text

        self.setup_ui()
        self.setup_connections()
        self.populate_data()

    def setup_ui(self):
        """设置对话框UI"""
        self.setWindowTitle("小说连贯性检查报告")
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)

        # 主布局
        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("📊 小说连贯性检查报告")
        title_label.setObjectName("DialogTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # 左侧：分数概览和问题列表
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)

        # 右侧：详细报告
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)

        # 设置分割器比例
        splitter.setSizes([400, 500])

        # 底部按钮
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)

    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 分数概览
        scores_group = self.create_scores_group()
        left_layout.addWidget(scores_group)

        # 问题列表
        issues_group = self.create_issues_group()
        left_layout.addWidget(issues_group)

        return left_widget

    def create_scores_group(self) -> QGroupBox:
        """创建分数概览组"""
        scores_group = QGroupBox("📈 质量分数概览")
        scores_layout = QVBoxLayout(scores_group)

        # 总体分数
        overall_layout = QHBoxLayout()
        overall_label = QLabel("总体质量:")
        overall_score_label = QLabel(f"{self.scores.overall_score:.1f}/100")
        overall_score_label.setObjectName("OverallScore")
        overall_score_label.setAlignment(Qt.AlignRight)

        # 根据分数设置颜色
        if self.scores.overall_score >= 80:
            overall_score_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
        elif self.scores.overall_score >= 60:
            overall_score_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 16px;")
        else:
            overall_score_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 16px;")

        overall_layout.addWidget(overall_label)
        overall_layout.addWidget(overall_score_label)
        scores_layout.addLayout(overall_layout)

        # 分项分数
        scores_details = [
            ("情节连贯度", self.scores.plot_continuity, "plot"),
            ("角色一致性", self.scores.character_consistency, "character"),
            ("设定连贯度", self.scores.setting_consistency, "setting")
        ]

        for name, score, score_type in scores_details:
            score_layout = QHBoxLayout()
            score_label = QLabel(f"{name}:")
            score_value_label = QLabel(f"{score:.1f}/100")
            score_value_label.setAlignment(Qt.AlignRight)

            # 设置颜色
            if score >= 80:
                color = "#4CAF50"
            elif score >= 60:
                color = "#FF9800"
            else:
                color = "#F44336"
            score_value_label.setStyleSheet(f"color: {color}; font-weight: bold;")

            # 进度条
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(score))
            progress_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)

            score_layout.addWidget(score_label, 1)
            score_layout.addWidget(progress_bar, 2)
            score_layout.addWidget(score_value_label, 1)
            scores_layout.addLayout(score_layout)

        return scores_group

    def create_issues_group(self) -> QGroupBox:
        """创建问题列表组"""
        issues_group = QGroupBox(f"🔍 问题详情 (共 {len(self.issues)} 个)")
        issues_layout = QVBoxLayout(issues_group)

        # 问题树形列表
        self.issues_tree = QTreeWidget()
        self.issues_tree.setHeaderLabels(["类型", "严重程度", "描述", "位置"])
        issues_layout.addWidget(self.issues_tree)

        return issues_group

    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 详细报告标题
        report_title = QLabel("📝 详细报告")
        report_title.setObjectName("SectionTitle")
        right_layout.addWidget(report_title)

        # 报告文本区域
        self.report_text_edit = QTextEdit()
        self.report_text_edit.setReadOnly(True)
        self.report_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        right_layout.addWidget(self.report_text_edit)

        return right_widget

    def create_button_layout(self) -> QHBoxLayout:
        """创建按钮布局"""
        button_layout = QHBoxLayout()

        # 导出按钮
        export_btn = QPushButton("📄 导出报告")
        export_btn.setObjectName("PrimaryButton")
        export_btn.clicked.connect(self.export_report)

        # 重新检查按钮
        recheck_btn = QPushButton("🔄 重新检查")
        recheck_btn.setObjectName("SecondaryButton")
        recheck_btn.clicked.connect(self.recheck_requested)

        # 关闭按钮
        close_btn = QPushButton("✖️ 关闭")
        close_btn.setObjectName("CloseButton")
        close_btn.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        button_layout.addWidget(recheck_btn)
        button_layout.addWidget(close_btn)

        return button_layout

    def setup_connections(self):
        """设置信号连接"""
        # 双击问题项跳转到详细报告对应位置
        self.issues_tree.itemDoubleClicked.connect(self.jump_to_issue_in_report)

    def populate_data(self):
        """填充数据"""
        # 填充问题列表
        self.populate_issues_tree()

        # 设置报告文本
        self.report_text_edit.setMarkdown(self.report_text)

    def populate_issues_tree(self):
        """填充问题树形列表"""
        # 按类型分组问题
        issues_by_type = {}
        for issue in self.issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)

        # 类型名称映射
        type_names = {
            'plot': '情节',
            'character_name': '角色名字',
            'character_trait': '角色特征',
            'setting': '设定'
        }

        # 严重程度图标映射
        severity_icons = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }

        # 创建树形结构
        for issue_type, issues in issues_by_type.items():
            type_item = QTreeWidgetItem(self.issues_tree)
            type_item.setText(0, f"{type_names.get(issue_type, issue_type)} ({len(issues)})")
            type_item.setExpanded(True)

            for issue in issues:
                issue_item = QTreeWidgetItem(type_item)
                issue_item.setText(0, severity_icons.get(issue.severity, ''))
                issue_item.setText(1, issue.severity)
                issue_item.setText(2, issue.description[:50] + "..." if len(issue.description) > 50 else issue.description)
                issue_item.setText(3, issue.location)

                # 存储完整问题信息
                issue_item.setData(0, Qt.UserRole, issue)

                # 根据严重程度设置颜色
                if issue.severity == 'high':
                    issue_item.setForeground(1, Qt.red)
                elif issue.severity == 'medium':
                    issue_item.setForeground(1, Qt.darkYellow)

    def jump_to_issue_in_report(self, item: QTreeWidgetItem, column: int):
        """跳转到报告中对应问题的位置"""
        issue_data = item.data(0, Qt.UserRole)
        if not issue_data:
            return

        # 在报告中搜索问题描述
        cursor = self.report_text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start)

        # 搜索问题关键词
        search_text = issue_data.description[:20]  # 使用前20个字符搜索
        found = self.report_text_edit.find(search_text)

        if found:
            # 高亮显示找到的文本
            cursor = self.report_text_edit.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)
            format = cursor.charFormat()
            format.setBackground(Qt.yellow)
            cursor.setCharFormat(format)

    def export_report(self):
        """导出报告到文件"""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出连贯性检查报告",
            "coherence_report.md",
            "Markdown文件 (*.md);;所有文件 (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.report_text)

                # 显示成功消息
                from ui_qt.widgets.status_bar import StatusBar
                if hasattr(self.parent(), 'status_bar'):
                    self.parent().status_bar.show_message(f"报告已导出到: {file_path}", 3000)

            except Exception as e:
                # 显示错误消息
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "导出失败", f"导出报告时出错:\n{str(e)}")

    def recheck_requested(self):
        """发出重新检查信号"""
        self.accept()  # 关闭对话框
        # 父窗口需要监听这个信号来重新执行检查


class CoherenceProgressDialog(QDialog):
    """连贯性检查进度对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("连贯性检查")
        self.setFixedSize(400, 150)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("正在进行连贯性检查...")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 无限进度条
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("正在分析章节内容...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def update_status(self, message: str):
        """更新状态消息"""
        self.status_label.setText(message)

    def set_progress(self, current: int, total: int):
        """设置进度"""
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)