# ui_qt/dialogs/role_import_dialog.py
# -*- coding: utf-8 -*-
"""
角色导入对话框
用于从外部文件或资源导入角色信息
"""

import os
import json
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QCheckBox,
    QFileDialog, QMessageBox, QComboBox, QFormLayout,
    QSplitter, QFrame, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)


class RoleImportDialog(QDialog):
    """角色导入对话框"""

    # 信号定义
    roles_imported = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_roles = []
        self.available_roles = []
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("导入角色")
        self.setModal(True)
        self.resize(700, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建标题
        title_label = QLabel(" 导入角色信息")
        set_font_size(title_label, 14, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("ImportTitleLabel")
        title_label.setStyleSheet("""
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # 左侧：文件选择和预览
        left_widget = self.create_file_selection_widget()
        main_splitter.addWidget(left_widget)

        # 右侧：角色选择和导入设置
        right_widget = self.create_role_selection_widget()
        main_splitter.addWidget(right_widget)

        # 设置分割器比例
        main_splitter.setSizes([300, 400])

        # 底部按钮
        self.create_bottom_buttons(layout)

    def create_file_selection_widget(self) -> QWidget:
        """创建文件选择区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 文件选择
        file_group = QGroupBox(" 选择文件")
        file_layout = QFormLayout(file_group)

        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("选择要导入的角色文件...")
        file_layout.addRow("文件路径:", self.create_file_selector())

        self.import_format = QComboBox()
        self.import_format.addItems([
            "JSON格式 (.json)",
            "CSV格式 (.csv)",
            "TXT格式 (.txt)",
            "Excel格式 (.xlsx)",
            "XML格式 (.xml)"
        ])
        file_layout.addRow("文件格式:", self.import_format)

        layout.addWidget(file_group)

        # 文件预览
        preview_group = QGroupBox(" 文件预览")
        preview_layout = QVBoxLayout(preview_group)

        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        self.file_preview.setStyleSheet("font-family: 'Courier New', monospace; font-size: 9pt;")
        self.file_preview.setPlaceholderText("文件内容预览将在此显示...")
        preview_layout.addWidget(self.file_preview)

        layout.addWidget(preview_group)

        # 导入选项
        options_group = QGroupBox(" 导入选项")
        options_layout = QVBoxLayout(options_group)

        self.overwrite_existing = QCheckBox("覆盖同名角色")
        self.overwrite_existing.setToolTip("如果已存在同名角色，是否覆盖")
        options_layout.addWidget(self.overwrite_existing)

        self.import_relationships = QCheckBox("导入角色关系")
        self.import_relationships.setChecked(True)
        self.import_relationships.setToolTip("同时导入角色之间的关系数据")
        options_layout.addWidget(self.import_relationships)

        self.validate_data = QCheckBox("验证数据格式")
        self.validate_data.setChecked(True)
        self.validate_data.setToolTip("导入前验证数据格式是否正确")
        options_layout.addWidget(self.validate_data)

        layout.addWidget(options_group)

        return widget

    def create_role_selection_widget(self) -> QWidget:
        """创建角色选择区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 搜索过滤
        search_group = QGroupBox(" 搜索和过滤")
        search_layout = QHBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入角色名或特征...")
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("")
        self.search_btn.clicked.connect(self.filter_roles)
        search_layout.addWidget(self.search_btn)

        self.clear_filter_btn = QPushButton("")
        self.clear_filter_btn.setToolTip("清除过滤")
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        search_layout.addWidget(self.clear_filter_btn)

        layout.addWidget(search_group)

        # 角色列表
        list_group = QGroupBox(" 可导入角色")
        list_layout = QVBoxLayout(list_group)

        # 列表控制
        control_layout = QHBoxLayout()

        self.select_all_btn = QPushButton(" 全选")
        self.select_all_btn.clicked.connect(self.select_all_roles)
        control_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton(" 全不选")
        self.deselect_all_btn.clicked.connect(self.deselect_all_roles)
        control_layout.addWidget(self.deselect_all_btn)

        self.invert_selection_btn = QPushButton(" 反选")
        self.invert_selection_btn.clicked.connect(self.invert_selection)
        control_layout.addWidget(self.invert_selection_btn)

        control_layout.addStretch()
        list_layout.addLayout(control_layout)

        # 角色树形列表
        self.role_tree = QTreeWidget()
        self.role_tree.setHeaderLabels(["选择", "角色名", "类型", "描述"])
        self.role_tree.itemChanged.connect(self.on_tree_item_changed)
        list_layout.addWidget(self.role_tree)

        layout.addWidget(list_group)

        # 选中角色统计
        stats_group = QGroupBox("📊 选择统计")
        stats_layout = QVBoxLayout(stats_group)

        stats_info = QHBoxLayout()
        stats_info.addWidget(QLabel("已选择:"))
        self.selected_count_label = QLabel("0")
        stats_info.addWidget(self.selected_count_label)

        stats_info.addWidget(QLabel("总计:"))
        self.total_count_label = QLabel("0")
        stats_info.addWidget(self.total_count_label)

        stats_info.addStretch()
        stats_layout.addLayout(stats_info)

        layout.addWidget(stats_group)

        return widget

    def create_file_selector(self) -> QWidget:
        """创建文件选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.file_path)

        browse_btn = QPushButton(" 浏览")
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn)

        preview_btn = QPushButton(" 预览")
        preview_btn.clicked.connect(self.preview_file)
        layout.addWidget(preview_btn)

        return widget

    def create_bottom_buttons(self, layout: QVBoxLayout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.import_btn = QPushButton(" 导入选中角色")
        self.import_btn.clicked.connect(self.import_selected_roles)
        self.import_btn.setObjectName("ImportRoleButton")
        self.import_btn.setProperty("style", "success")
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)

        self.cancel_btn = QPushButton(" 取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addWidget(button_layout)

    def browse_file(self):
        """浏览文件"""
        file_filter = "所有支持格式 (*.json *.csv *.txt *.xlsx *.xml);;JSON文件 (*.json);;CSV文件 (*.csv);;文本文件 (*.txt);;Excel文件 (*.xlsx);;XML文件 (*.xml)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择角色文件", "", file_filter
        )

        if file_path:
            self.file_path.setText(file_path)
            self.detect_file_format(file_path)
            self.preview_file()

    def detect_file_format(self, file_path: str):
        """自动检测文件格式"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        format_map = {
            '.json': "JSON格式 (.json)",
            '.csv': "CSV格式 (.csv)",
            '.txt': "TXT格式 (.txt)",
            '.xlsx': "Excel格式 (.xlsx)",
            '.xls': "Excel格式 (.xlsx)",
            '.xml': "XML格式 (.xml)"
        }

        if ext in format_map:
            self.import_format.setCurrentText(format_map[ext])

    def preview_file(self):
        """预览文件内容"""
        file_path = self.file_path.text()
        if not file_path or not os.path.exists(file_path):
            show_error_dialog(self, "错误", "请选择有效的文件")
            return

        try:
            format_name = self.import_format.currentText()

            if "JSON" in format_name:
                self.preview_json_file(file_path)
            elif "CSV" in format_name:
                self.preview_csv_file(file_path)
            elif "TXT" in format_name:
                self.preview_txt_file(file_path)
            else:
                self.preview_text_file(file_path)

        except Exception as e:
            show_error_dialog(self, "错误", f"预览文件失败: {str(e)}")

    def preview_json_file(self, file_path: str):
        """预览JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                self.available_roles = data
                self.display_roles_in_tree(data)
            elif isinstance(data, dict) and 'roles' in data:
                self.available_roles = data['roles']
                self.display_roles_in_tree(data['roles'])
            else:
                # 单个角色
                self.available_roles = [data]
                self.display_roles_in_tree([data])

            # 显示预览
            preview_text = json.dumps(data, ensure_ascii=False, indent=2)
            if len(preview_text) > 2000:
                preview_text = preview_text[:2000] + "\n... (截断)"
            self.file_preview.setPlainText(preview_text)

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {str(e)}")

    def preview_csv_file(self, file_path: str):
        """预览CSV文件"""
        import csv

        roles = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 将CSV行转换为角色字典
                role = {
                    'name': row.get('name', row.get('角色名', '')),
                    'type': row.get('type', row.get('类型', '其他')),
                    'gender': row.get('gender', row.get('性别', '')),
                    'age': row.get('age', row.get('年龄', '')),
                    'appearance': row.get('appearance', row.get('外貌', '')),
                    'personality': row.get('personality', row.get('性格', '')),
                    'background': row.get('background', row.get('背景', ''))
                }
                if role['name']:  # 只包含有名称的角色
                    roles.append(role)

        self.available_roles = roles
        self.display_roles_in_tree(roles)

        # 显示预览
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            if len(content) > 2000:
                content = content[:2000] + "\n... (截断)"
            self.file_preview.setPlainText(content)

    def preview_txt_file(self, file_path: str):
        """预览TXT文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尝试解析TXT格式的角色数据
        roles = self.parse_txt_roles(content)
        self.available_roles = roles
        self.display_roles_in_tree(roles)

        # 显示预览
        if len(content) > 2000:
            content = content[:2000] + "\n... (截断)"
        self.file_preview.setPlainText(content)

    def preview_text_file(self, file_path: str):
        """预览文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if len(content) > 2000:
            content = content[:2000] + "\n... (截断)"
        self.file_preview.setPlainText(content)

    def parse_txt_roles(self, content: str) -> List[Dict[str, Any]]:
        """解析TXT格式的角色数据"""
        roles = []
        lines = content.split('\n')
        current_role = {}

        for line in lines:
            line = line.strip()
            if not line:
                if current_role:
                    roles.append(current_role)
                    current_role = {}
                continue

            if '：' in line:
                key, value = line.split('：', 1)
                key = key.strip()
                value = value.strip()

                if key in ['姓名', '名字', '角色名']:
                    current_role['name'] = value
                elif key in ['类型', '角色类型']:
                    current_role['type'] = value
                elif key in ['性别']:
                    current_role['gender'] = value
                elif key in ['年龄']:
                    current_role['age'] = value
                elif key in ['外貌', '外貌描述']:
                    current_role['appearance'] = value
                elif key in ['性格', '性格特征']:
                    current_role['personality'] = value
                elif key in ['背景', '背景故事']:
                    current_role['background'] = value

        # 添加最后一个角色
        if current_role:
            roles.append(current_role)

        return roles

    def display_roles_in_tree(self, roles: List[Dict[str, Any]]):
        """在树形控件中显示角色"""
        self.role_tree.clear()
        self.selected_roles = []

        for i, role in enumerate(roles):
            name = role.get('name', f'角色{i+1}')
            role_type = role.get('type', '其他')
            description = role.get('appearance', role.get('personality', ''))[:50]
            if len(description) == 50:
                description += '...'

            # 创建检查项
            check_item = QTreeWidgetItem(self.role_tree)
            check_item.setCheckState(0, Qt.Unchecked)
            check_item.setText(1, name)
            check_item.setText(2, role_type)
            check_item.setText(3, description)

            # 存储角色数据
            check_item.setData(0, Qt.UserRole, role)

        self.update_statistics()
        self.import_btn.setEnabled(len(roles) > 0)

    def on_tree_item_changed(self, item: QTreeWidgetItem, column: int):
        """树形项变更处理"""
        if column == 0:  # 选择列
            role = item.data(0, Qt.UserRole)
            if item.checkState(0) == Qt.Checked:
                if role not in self.selected_roles:
                    self.selected_roles.append(role)
            else:
                if role in self.selected_roles:
                    self.selected_roles.remove(role)

            self.update_statistics()

    def update_statistics(self):
        """更新统计信息"""
        total_count = self.role_tree.topLevelItemCount()
        selected_count = len(self.selected_roles)

        self.total_count_label.setText(str(total_count))
        self.selected_count_label.setText(str(selected_count))

    def filter_roles(self):
        """过滤角色"""
        filter_text = self.search_input.text().lower()
        if not filter_text:
            # 显示所有项
            for i in range(self.role_tree.topLevelItemCount()):
                self.role_tree.topLevelItem(i).setHidden(False)
            return

        # 隐藏不匹配的项
        for i in range(self.role_tree.topLevelItemCount()):
            item = self.role_tree.topLevelItem(i)
            name = item.text(1).lower()
            role_type = item.text(2).lower()
            description = item.text(3).lower()

            if filter_text in name or filter_text in role_type or filter_text in description:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def clear_filter(self):
        """清除过滤"""
        self.search_input.clear()
        self.filter_roles()

    def select_all_roles(self):
        """全选角色"""
        for i in range(self.role_tree.topLevelItemCount()):
            item = self.role_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Checked)

    def deselect_all_roles(self):
        """全不选角色"""
        for i in range(self.role_tree.topLevelItemCount()):
            item = self.role_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Unchecked)

    def invert_selection(self):
        """反选"""
        for i in range(self.role_tree.topLevelItemCount()):
            item = self.role_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                item.setCheckState(0, Qt.Unchecked)
            else:
                item.setCheckState(0, Qt.Checked)

    def import_selected_roles(self):
        """导入选中的角色"""
        if not self.selected_roles:
            show_error_dialog(self, "错误", "请选择要导入的角色")
            return

        # 验证数据（如果开启）
        if self.validate_data.isChecked():
            if not self.validate_roles_data(self.selected_roles):
                return

        # 发送导入信号
        self.roles_imported.emit(self.selected_roles)
        show_info_dialog(self, "成功", f"已导入 {len(self.selected_roles)} 个角色")
        self.accept()

    def validate_roles_data(self, roles: List[Dict[str, Any]]) -> bool:
        """验证角色数据"""
        for i, role in enumerate(roles):
            if not role.get('name', '').strip():
                show_error_dialog(self, "验证错误", f"第 {i+1} 个角色缺少名称")
                return False

            # 可以添加更多验证规则
            # 检查必需字段、数据类型等

        return True

    def get_imported_roles(self) -> List[Dict[str, Any]]:
        """获取导入的角色列表"""
        return self.selected_roles.copy()