# ui_qt/widgets/role_manager.py
# -*- coding: utf-8 -*-
"""
角色管理组件
提供角色创建、编辑、导入导出等功能的现代化界面
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QFrame, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QTabWidget, QProgressBar,
    QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help
)


class RoleManager(QWidget):
    """角色管理组件"""

    # 信号定义
    role_selected = Signal(str)
    role_changed = Signal(str, dict)
    role_created = Signal(str, dict)
    role_deleted = Signal(str)

    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.current_role = ""
        self.current_project_path = ""
        self.setup_ui()
        self.load_sample_data()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建标题
        title_label = QLabel("👥 角色管理器")
        set_font_size(title_label, 14, bold=True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #f3e5f5; border-radius: 6px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # 左侧：角色库和分类
        left_widget = self.create_role_library_widget()
        main_splitter.addWidget(left_widget)

        # 右侧：角色详情编辑
        right_widget = self.create_role_editor_widget()
        main_splitter.addWidget(right_widget)

        # 设置分割器比例
        main_splitter.setSizes([350, 650])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        # 底部操作栏
        self.create_bottom_actions(layout)

    def create_role_library_widget(self) -> QWidget:
        """创建角色库导航区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 搜索栏
        search_group = QGroupBox("🔍 角色搜索")
        search_layout = QHBoxLayout(search_group)

        self.role_search = QLineEdit()
        self.role_search.setPlaceholderText("输入角色名、标签或特征...")
        self.role_search.textChanged.connect(self.filter_roles)
        search_layout.addWidget(self.role_search)

        self.search_btn = QPushButton("🔍")
        self.search_btn.clicked.connect(self.search_roles)
        search_layout.addWidget(self.search_btn)

        layout.addWidget(search_group)

        # 角色分类树
        category_group = QGroupBox("📂 角色分类")
        category_layout = QVBoxLayout(category_group)

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.itemClicked.connect(self.on_category_selected)
        category_layout.addWidget(self.category_tree)

        # 分类操作按钮
        category_btn_layout = QHBoxLayout()

        self.add_category_btn = QPushButton("➕")
        self.add_category_btn.setToolTip("添加分类")
        self.add_category_btn.clicked.connect(self.add_category)
        category_btn_layout.addWidget(self.add_category_btn)

        self.edit_category_btn = QPushButton("✏️")
        self.edit_category_btn.setToolTip("编辑分类")
        self.edit_category_btn.clicked.connect(self.edit_category)
        category_btn_layout.addWidget(self.edit_category_btn)

        self.delete_category_btn = QPushButton("🗑️")
        self.delete_category_btn.setToolTip("删除分类")
        self.delete_category_btn.clicked.connect(self.delete_category)
        category_btn_layout.addWidget(self.delete_category_btn)

        category_btn_layout.addStretch()
        category_layout.addLayout(category_btn_layout)

        layout.addWidget(category_group)

        # 角色列表
        list_group = QGroupBox("👥 角色列表")
        list_layout = QVBoxLayout(list_group)

        # 列表视图切换
        view_switch = QHBoxLayout()
        self.grid_view_btn = QPushButton("⚏")
        self.grid_view_btn.setCheckable(True)
        self.grid_view_btn.setChecked(True)
        self.grid_view_btn.setToolTip("网格视图")
        self.grid_view_btn.clicked.connect(lambda: self.switch_view("grid"))
        view_switch.addWidget(self.grid_view_btn)

        self.list_view_btn = QPushButton("☰")
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.setToolTip("列表视图")
        self.list_view_btn.clicked.connect(lambda: self.switch_view("list"))
        view_switch.addWidget(self.list_view_btn)

        view_switch.addStretch()
        list_layout.addLayout(view_switch)

        # 角色网格视图
        self.role_grid = QWidget()
        self.role_grid_layout = QGridLayout(self.role_grid)
        self.role_grid_layout.setSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.role_grid)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        list_layout.addWidget(scroll_area)

        # 角色列表视图（默认隐藏）
        self.role_list = QListWidget()
        self.role_list.itemClicked.connect(self.on_role_item_clicked)
        self.role_list.hide()
        list_layout.addWidget(self.role_list)

        layout.addWidget(list_group)

        # 快速统计
        stats_group = QGroupBox("📊 快速统计")
        stats_layout = QFormLayout(stats_group)

        self.total_roles_label = QLabel("0")
        stats_layout.addRow("总角色数:", self.total_roles_label)

        self.main_roles_label = QLabel("0")
        stats_layout.addRow("主要角色:", self.main_roles_label)

        self.minor_roles_label = QLabel("0")
        stats_layout.addRow("次要角色:", self.minor_roles_label)

        layout.addWidget(stats_group)

        return widget

    def create_role_editor_widget(self) -> QWidget:
        """创建角色编辑区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 角色基本信息
        self.create_basic_info_section(layout)

        # 详细属性设置
        self.create_attributes_section(layout)

        # 角色关系网络
        self.create_relationships_section(layout)

        # 角色背景故事
        self.create_background_section(layout)

        return widget

    def create_basic_info_section(self, layout: QVBoxLayout):
        """创建基本信息区域"""
        basic_group = QGroupBox("📋 基本信息")
        basic_layout = QFormLayout(basic_group)

        # 角色名称
        name_layout = QHBoxLayout()
        self.role_name = QLineEdit()
        self.role_name.setPlaceholderText("输入角色名称...")
        self.role_name.textChanged.connect(self.on_basic_info_changed)
        name_layout.addWidget(self.role_name)

        self.role_avatar = QPushButton("🖼️")
        self.role_avatar.setToolTip("选择角色头像")
        self.role_avatar.clicked.connect(self.select_avatar)
        name_layout.addWidget(self.role_avatar)

        basic_layout.addRow("角色名称:", name_layout)

        # 角色类型
        self.role_type = QComboBox()
        self.role_type.addItems([
            "主角", "配角", "反派", "路人", "导师", "朋友", "恋人", "家人", "敌人", "其他"
        ])
        basic_layout.addRow("角色类型:", self.role_type)

        # 性别
        self.role_gender = QComboBox()
        self.role_gender.addItems(["男", "女", "其他", "未知"])
        basic_layout.addRow("性别:", self.role_gender)

        # 年龄
        age_layout = QHBoxLayout()
        self.role_age = QSpinBox()
        self.role_age.setRange(0, 10000)
        self.role_age.setValue(20)
        age_layout.addWidget(self.role_age)

        self.age_unit = QComboBox()
        self.age_unit.addItems(["岁", "月", "未知"])
        age_layout.addWidget(self.age_unit)

        basic_layout.addRow("年龄:", age_layout)

        # 外貌描述
        self.role_appearance = QTextEdit()
        self.role_appearance.setMaximumHeight(80)
        self.role_appearance.setPlaceholderText("描述角色的外貌特征...")
        self.role_appearance.textChanged.connect(self.on_basic_info_changed)
        basic_layout.addRow("外貌描述:", self.role_appearance)

        layout.addWidget(basic_group)

    def create_attributes_section(self, layout: QVBoxLayout):
        """创建属性设置区域"""
        attr_group = QGroupBox("⚡ 角色属性")
        attr_layout = QVBoxLayout(attr_group)

        # 属性编辑标签页
        attr_tabs = QTabWidget()
        attr_layout.addWidget(attr_tabs)

        # 性格标签页
        self.create_personality_tab(attr_tabs)

        # 能力标签页
        self.create_abilities_tab(attr_tabs)

        # 背景标签页
        self.create_background_info_tab(attr_tabs)

        layout.addWidget(attr_group)

    def create_personality_tab(self, parent):
        """创建性格标签页"""
        personality_widget = QWidget()
        layout = QGridLayout(personality_widget)

        # 性格特质网格
        personality_traits = [
            "勇敢", "善良", "聪明", "幽默", "冷静", "冲动",
            "乐观", "悲观", "外向", "内向", "正直", "狡猾",
            "温柔", "严厉", "自信", "自卑", "独立", "依赖",
            "诚实", "虚伪", "慷慨", "自私", "耐心", "急躁"
        ]

        self.personality_checkboxes = {}
        for i, trait in enumerate(personality_traits):
            row = i // 4
            col = i % 4

            checkbox = QCheckBox(trait)
            checkbox.stateChanged.connect(self.on_personality_changed)
            self.personality_checkboxes[trait] = checkbox
            layout.addWidget(checkbox, row, col)

        # 详细性格描述
        layout.addWidget(QLabel("详细性格描述:"), 6, 0, 1, 4)
        self.personality_description = QTextEdit()
        self.personality_description.setMaximumHeight(80)
        self.personality_description.setPlaceholderText("详细描述角色的性格特点和思维模式...")
        layout.addWidget(self.personality_description, 7, 0, 1, 4)

        parent.addTab(personality_widget, "🎭 性格")

    def create_abilities_tab(self, parent):
        """创建能力标签页"""
        abilities_widget = QWidget()
        layout = QVBoxLayout(abilities_widget)

        # 技能列表
        skills_group = QGroupBox("💪 技能和能力")
        skills_layout = QVBoxLayout(skills_group)

        self.abilities_list = QListWidget()
        self.abilities_list.setMaximumHeight(150)
        skills_layout.addWidget(self.abilities_list)

        # 技能操作按钮
        skill_btn_layout = QHBoxLayout()

        self.add_ability_btn = QPushButton("➕ 添加技能")
        self.add_ability_btn.clicked.connect(self.add_ability)
        skill_btn_layout.addWidget(self.add_ability_btn)

        self.remove_ability_btn = QPushButton("➖ 移除技能")
        self.remove_ability_btn.clicked.connect(self.remove_ability)
        skill_btn_layout.addWidget(self.remove_ability_btn)

        skill_btn_layout.addStretch()
        skills_layout.addLayout(skill_btn_layout)

        layout.addWidget(skills_group)

        # 特殊能力
        special_group = QGroupBox("✨ 特殊能力")
        special_layout = QVBoxLayout(special_group)

        self.special_abilities = QTextEdit()
        self.special_abilities.setMaximumHeight(100)
        self.special_abilities.setPlaceholderText("描述角色的特殊能力、魔法、超能力等...")
        special_layout.addWidget(self.special_abilities)

        layout.addWidget(special_group)

        # 弱点和限制
        weakness_group = QGroupBox("⚠️ 弱点和限制")
        weakness_layout = QVBoxLayout(weakness_group)

        self.weaknesses = QTextEdit()
        self.weaknesses.setMaximumHeight(80)
        self.weaknesses.setPlaceholderText("描述角色的弱点、恐惧、限制等...")
        weakness_layout.addWidget(self.weaknesses)

        layout.addWidget(weakness_group)

        parent.addTab(abilities_widget, "⚡ 能力")

    def create_background_info_tab(self, parent):
        """创建背景信息标签页"""
        background_widget = QWidget()
        layout = QVBoxLayout(background_widget)

        # 出身信息
        origin_group = QGroupBox("🏠 出身背景")
        origin_layout = QFormLayout(origin_group)

        self.role_birthplace = QLineEdit()
        self.role_birthplace.setPlaceholderText("出生地点...")
        origin_layout.addRow("出生地点:", self.role_birthplace)

        self.role_family = QLineEdit()
        self.role_family.setPlaceholderText("家庭成员...")
        origin_layout.addRow("家庭背景:", self.role_family)

        self.role_occupation = QLineEdit()
        self.role_occupation.setPlaceholderText("职业或身份...")
        origin_layout.addRow("职业身份:", self.role_occupation)

        layout.addWidget(origin_group)

        # 教育经历
        education_group = QGroupBox("🎓 教育经历")
        education_layout = QVBoxLayout(education_group)

        self.education_history = QTextEdit()
        self.education_history.setMaximumHeight(80)
        self.education_history.setPlaceholderText("描述角色的教育背景和重要学习经历...")
        education_layout.addWidget(self.education_history)

        layout.addWidget(education_group)

        parent.addTab(background_widget, "📚 背景")

    def create_relationships_section(self, layout: QVBoxLayout):
        """创建角色关系区域"""
        relation_group = QGroupBox("🔗 角色关系")
        relation_layout = QVBoxLayout(relation_group)

        # 关系网络视图
        self.relationship_view = QTreeWidget()
        self.relationship_view.setHeaderLabels(["关系", "角色", "描述"])
        relation_layout.addWidget(self.relationship_view)

        # 关系操作按钮
        relation_btn_layout = QHBoxLayout()

        self.add_relation_btn = QPushButton("➕ 添加关系")
        self.add_relation_btn.clicked.connect(self.add_relationship)
        relation_btn_layout.addWidget(self.add_relation_btn)

        self.edit_relation_btn = QPushButton("✏️ 编辑关系")
        self.edit_relation_btn.clicked.connect(self.edit_relationship)
        relation_btn_layout.addWidget(self.edit_relation_btn)

        self.delete_relation_btn = QPushButton("🗑️ 删除关系")
        self.delete_relation_btn.clicked.connect(self.delete_relationship)
        relation_btn_layout.addWidget(self.delete_relation_btn)

        relation_btn_layout.addStretch()
        relation_layout.addLayout(relation_btn_layout)

        layout.addWidget(relation_group)

    def create_background_section(self, layout: QVBoxLayout):
        """创建背景故事区域"""
        story_group = QGroupBox("📖 背景故事")
        story_layout = QVBoxLayout(story_group)

        # 背景故事编辑器
        self.background_story = QTextEdit()
        self.background_story.setPlaceholderText("详细描述角色的背景故事、成长经历、重要事件等...")
        story_layout.addWidget(self.background_story)

        # 故事提示
        story_tips = QLabel("💡 提示: 可以包含角色的童年经历、重要转折点、性格形成原因等")
        story_tips.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        story_layout.addWidget(story_tips)

        layout.addWidget(story_group)

    def create_bottom_actions(self, layout: QVBoxLayout):
        """创建底部操作栏"""
        action_group = QFrame()
        action_group.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        action_layout = QHBoxLayout(action_group)

        # 左侧操作
        self.new_role_btn = QPushButton("➕ 新建角色")
        self.new_role_btn.clicked.connect(self.create_new_role)
        action_layout.addWidget(self.new_role_btn)

        self.save_role_btn = QPushButton("💾 保存角色")
        self.save_role_btn.clicked.connect(self.save_current_role)
        self.save_role_btn.setStyleSheet("font-weight: bold; background-color: #4caf50; color: white;")
        action_layout.addWidget(self.save_role_btn)

        self.delete_role_btn = QPushButton("🗑️ 删除角色")
        self.delete_role_btn.clicked.connect(self.delete_current_role)
        self.delete_role_btn.setStyleSheet("background-color: #f44336; color: white;")
        action_layout.addWidget(self.delete_role_btn)

        action_layout.addWidget(create_separator("vertical"))

        # 中间操作
        self.duplicate_role_btn = QPushButton("📋 复制角色")
        self.duplicate_role_btn.clicked.connect(self.duplicate_role)
        action_layout.addWidget(self.duplicate_role_btn)

        self.export_role_btn = QPushButton("📤 导出角色")
        self.export_role_btn.clicked.connect(self.export_role)
        action_layout.addWidget(self.export_role_btn)

        self.import_role_btn = QPushButton("📥 导入角色")
        self.import_role_btn.clicked.connect(self.import_role)
        action_layout.addWidget(self.import_role_btn)

        action_layout.addStretch()

        # 右侧操作
        self.generate_ai_btn = QPushButton("🤖 AI生成角色")
        self.generate_ai_btn.clicked.connect(self.generate_ai_role)
        self.generate_ai_btn.setStyleSheet("background-color: #2196f3; color: white;")
        action_layout.addWidget(self.generate_ai_btn)

        layout.addWidget(action_group)

    def load_sample_data(self):
        """加载示例数据"""
        # 添加分类
        categories = ["主要角色", "次要角色", "配角", "反派", "路人"]
        for category in categories:
            item = QTreeWidgetItem(self.category_tree, [category])
            item.setIcon(0, QIcon())  # 这里可以添加图标

        # 添加示例角色
        self.add_role_to_grid("主角张三", "主要角色")
        self.add_role_to_grid("导师李四", "主要角色")
        self.add_role_to_grid("反派王五", "反派")
        self.add_role_to_grid("朋友赵六", "配角")

        # 更新统计
        self.update_statistics()

    def add_role_to_grid(self, name: str, category: str):
        """添加角色到网格视图"""
        # 创建角色卡片
        role_card = self.create_role_card(name, category)

        # 计算网格位置
        count = self.role_grid_layout.count()
        row = count // 2
        col = count % 2

        self.role_grid_layout.addWidget(role_card, row, col)

    def create_role_card(self, name: str, category: str) -> QWidget:
        """创建角色卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #2196f3;
                background-color: #f8f9fa;
            }
        """)
        card.setMinimumSize(150, 120)
        card.setMaximumSize(150, 120)

        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # 头像占位符
        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 24pt;")
        layout.addWidget(avatar)

        # 角色名称
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout.addWidget(name_label)

        # 角色类别
        category_label = QLabel(category)
        category_label.setAlignment(Qt.AlignCenter)
        category_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(category_label)

        # 点击事件
        card.mousePressEvent = lambda event: self.on_role_card_clicked(name, card)

        return card

    def on_role_card_clicked(self, name: str, card: QFrame):
        """角色卡片点击处理"""
        # 高亮选中的卡片
        for i in range(self.role_grid_layout.count()):
            widget = self.role_grid_layout.itemAt(i).widget()
            if isinstance(widget, QFrame):
                widget.setStyleSheet("""
                    QFrame {
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        background-color: white;
                        padding: 10px;
                    }
                """)

        card.setStyleSheet("""
            QFrame {
                border: 2px solid #2196f3;
                border-radius: 8px;
                background-color: #e3f2fd;
                padding: 10px;
            }
        """)

        # 加载角色详情
        self.load_role_details(name)
        self.current_role = name
        self.role_selected.emit(name)

    def load_role_details(self, name: str):
        """加载角色详情"""
        # 这里实现从数据源加载角色详情的逻辑
        # 暂时使用模拟数据
        self.role_name.setText(name)
        self.role_type.setCurrentText("主角")
        self.role_gender.setCurrentText("男")
        self.role_age.setValue(25)
        self.role_appearance.setPlainText("中等身材，黑色短发，眼神锐利...")
        self.background_story.setPlainText("出生于普通家庭，从小就展现出非凡的能力...")

    def on_category_selected(self, item: QTreeWidgetItem, column: int):
        """分类选择处理"""
        category_name = item.text(0)
        self.filter_by_category(category_name)

    def on_role_item_clicked(self, item: QListWidgetItem):
        """列表项点击处理"""
        role_name = item.text()
        self.load_role_details(role_name)
        self.current_role = role_name
        self.role_selected.emit(role_name)

    def filter_roles(self, text: str):
        """过滤角色"""
        # 这里实现搜索过滤逻辑
        pass

    def search_roles(self):
        """搜索角色"""
        search_text = self.role_search.text()
        # 这里实现搜索逻辑
        pass

    def filter_by_category(self, category: str):
        """按分类过滤"""
        # 这里实现分类过滤逻辑
        pass

    def switch_view(self, view_type: str):
        """切换视图"""
        if view_type == "grid":
            self.role_grid.show()
            self.role_list.hide()
            self.grid_view_btn.setChecked(True)
            self.list_view_btn.setChecked(False)
        else:
            self.role_grid.hide()
            self.role_list.show()
            self.grid_view_btn.setChecked(False)
            self.list_view_btn.setChecked(True)

    def on_basic_info_changed(self):
        """基本信息变更"""
        if self.current_role:
            self.role_changed.emit(self.current_role, self.get_role_data())

    def on_personality_changed(self):
        """性格变更"""
        if self.current_role:
            self.role_changed.emit(self.current_role, self.get_role_data())

    def get_role_data(self) -> Dict[str, Any]:
        """获取角色数据"""
        personalities = []
        for trait, checkbox in self.personality_checkboxes.items():
            if checkbox.isChecked():
                personalities.append(trait)

        return {
            "name": self.role_name.text(),
            "type": self.role_type.currentText(),
            "gender": self.role_gender.currentText(),
            "age": self.role_age.value(),
            "appearance": self.role_appearance.toPlainText(),
            "personalities": personalities,
            "personality_description": self.personality_description.toPlainText(),
            "background_story": self.background_story.toPlainText()
        }

    def create_new_role(self):
        """创建新角色"""
        # 清空编辑器
        self.clear_editor()
        self.current_role = ""
        self.role_name.setFocus()

    def save_current_role(self):
        """保存当前角色"""
        role_data = self.get_role_data()
        if not role_data["name"]:
            show_error_dialog(self, "错误", "请输入角色名称")
            return

        # 这里实现保存逻辑
        self.role_created.emit(role_data["name"], role_data)
        show_info_dialog(self, "成功", f"角色 '{role_data['name']}' 已保存")

    def delete_current_role(self):
        """删除当前角色"""
        if not self.current_role:
            show_error_dialog(self, "错误", "请先选择要删除的角色")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除角色 '{self.current_role}' 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.role_deleted.emit(self.current_role)
            self.clear_editor()
            show_info_dialog(self, "成功", f"角色 '{self.current_role}' 已删除")

    def clear_editor(self):
        """清空编辑器"""
        self.role_name.clear()
        self.role_type.setCurrentIndex(0)
        self.role_gender.setCurrentIndex(0)
        self.role_age.setValue(20)
        self.role_appearance.clear()
        self.personality_description.clear()
        self.background_story.clear()

        # 清空性格选择
        for checkbox in self.personality_checkboxes.values():
            checkbox.setChecked(False)

    def duplicate_role(self):
        """复制角色"""
        if not self.current_role:
            show_error_dialog(self, "错误", "请先选择要复制的角色")
            return

        # 这里实现复制逻辑
        show_info_dialog(self, "提示", "角色复制功能待实现")

    def export_role(self):
        """导出角色"""
        if not self.current_role:
            show_error_dialog(self, "错误", "请先选择要导出的角色")
            return

        # 这里实现导出逻辑
        show_info_dialog(self, "提示", "角色导出功能待实现")

    def import_role(self):
        """导入角色"""
        # 这里实现导入逻辑
        show_info_dialog(self, "提示", "角色导入功能待实现")

    def generate_ai_role(self):
        """AI生成角色"""
        # 这里实现AI生成逻辑
        show_info_dialog(self, "提示", "AI角色生成功能待实现")

    def add_category(self):
        """添加分类"""
        # 这里实现添加分类逻辑
        show_info_dialog(self, "提示", "添加分类功能待实现")

    def edit_category(self):
        """编辑分类"""
        # 这里实现编辑分类逻辑
        show_info_dialog(self, "提示", "编辑分类功能待实现")

    def delete_category(self):
        """删除分类"""
        # 这里实现删除分类逻辑
        show_info_dialog(self, "提示", "删除分类功能待实现")

    def add_ability(self):
        """添加技能"""
        # 这里实现添加技能逻辑
        show_info_dialog(self, "提示", "添加技能功能待实现")

    def remove_ability(self):
        """移除技能"""
        # 这里实现移除技能逻辑
        show_info_dialog(self, "提示", "移除技能功能待实现")

    def add_relationship(self):
        """添加关系"""
        # 这里实现添加关系逻辑
        show_info_dialog(self, "提示", "添加关系功能待实现")

    def edit_relationship(self):
        """编辑关系"""
        # 这里实现编辑关系逻辑
        show_info_dialog(self, "提示", "编辑关系功能待实现")

    def delete_relationship(self):
        """删除关系"""
        # 这里实现删除关系逻辑
        show_info_dialog(self, "提示", "删除关系功能待实现")

    def select_avatar(self):
        """选择头像"""
        # 这里实现选择头像逻辑
        show_info_dialog(self, "提示", "头像选择功能待实现")

    def update_statistics(self):
        """更新统计信息"""
        # 这里实现统计更新逻辑
        total_roles = 4  # 示例数据
        main_roles = 2   # 示例数据
        minor_roles = 2   # 示例数据

        self.total_roles_label.setText(str(total_roles))
        self.main_roles_label.setText(str(main_roles))
        self.minor_roles_label.setText(str(minor_roles))

    def load_project(self, project_path: str):
        """加载项目"""
        self.current_project_path = project_path
        # 这里实现项目加载逻辑