# ui_qt/widgets/role_manager.py
# -*- coding: utf-8 -*-
"""
角色管理组件
提供角色创建、编辑、导入导出等功能的现代化界面
"""

import threading
from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QGridLayout,
    QMessageBox, QCheckBox, QFrame, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QTabWidget, QProgressBar, QProgressDialog,
    QScrollArea, QSizePolicy, QDialog, QInputDialog
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from ..utils.ui_helpers import (
    create_separator, set_font_size, show_info_dialog,
    show_error_dialog, create_label_with_help, validate_required
)
from ..utils.tooltip_manager import tooltip_manager
from novel_generator.data_manager import DataManager


class RoleManager(QWidget):
    """角色管理组件"""

    # 信号定义
    role_selected = Signal(str)
    role_changed = Signal(str, dict)
    role_created = Signal(str, dict)
    role_deleted = Signal(str)

    def __init__(self, config: Dict[str, Any], data_manager=None, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.data_manager = data_manager
        self.current_role = ""
        self.current_project_path = ""
        self.pending_role_data = None  # 存储待处理的角色数据
        self.pending_role_data_lock = threading.Lock()  # 线程安全锁
        self.all_roles = {}  # 存储所有角色的数据 {name: {data}}
        self.current_filter = ""  # 当前过滤文本
        self.current_category = "全部"  # 当前分类过滤
        self.setup_ui()
        self.load_sample_data()

        # 使用事件循环启动后执行的定时器
        QTimer.singleShot(0, self._initialize_timer)

    def setup_ui(self):
        """设置UI布局"""
        import logging
        logger = logging.getLogger(__name__)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

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

        # 设置工具提示
        self.setup_tooltips()

        logger.info("UI布局完成")

    def _initialize_timer(self):
        """初始化定时器（在事件循环启动后执行）"""
        import logging
        logger = logging.getLogger(__name__)

        # 创建定时器用于定期轮询待处理的角色数据
        self.ui_update_timer = QTimer()
        self.ui_update_timer.setSingleShot(False)  # 改为重复定时器
        self.ui_update_timer.timeout.connect(self._check_pending_role_data)
        self.ui_update_timer.start(500)  # 每500ms轮询一次

        logger.info("[成功] 定时器初始化完成 - 每500ms轮询一次")

    def setup_tooltips(self):
        """设置工具提示"""
        # 角色基本信息
        if hasattr(self, 'role_name'):
            tooltip_manager.add_tooltip(self.role_name, "role_name")
        if hasattr(self, 'role_age'):
            tooltip_manager.add_tooltip(self.role_age, "role_age")
        if hasattr(self, 'role_description'):
            tooltip_manager.add_tooltip(self.role_description, "role_description")
        if hasattr(self, 'personality_description'):
            tooltip_manager.add_tooltip(self.personality_description, "personality")
        if hasattr(self, 'background_story'):
            tooltip_manager.add_tooltip(self.background_story, "background")

        # 底部操作按钮
        if hasattr(self, 'new_role_btn'):
            tooltip_manager.add_tooltip(self.new_role_btn, "new_role")
        if hasattr(self, 'save_role_btn'):
            tooltip_manager.add_tooltip(self.save_role_btn, "save_role")
        if hasattr(self, 'delete_role_btn'):
            tooltip_manager.add_tooltip(self.delete_role_btn, "delete_role")
        if hasattr(self, 'duplicate_role_btn'):
            tooltip_manager.add_tooltip(self.duplicate_role_btn, "copy_role")
        if hasattr(self, 'export_role_btn'):
            tooltip_manager.add_tooltip(self.export_role_btn, "export_role")
        if hasattr(self, 'import_role_btn'):
            tooltip_manager.add_tooltip(self.import_role_btn, "import_role")
        if hasattr(self, 'use_template_btn'):
            tooltip_manager.add_tooltip(self.use_template_btn, "use_template")
        if hasattr(self, 'save_as_template_btn'):
            tooltip_manager.add_tooltip(self.save_as_template_btn, "save_role")
        if hasattr(self, 'generate_ai_btn'):
            tooltip_manager.add_tooltip(self.generate_ai_btn, "ai_generate")

    def create_role_library_widget(self) -> QWidget:
        """创建角色库导航区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 搜索栏
        search_group = QGroupBox(" 角色搜索")
        search_layout = QHBoxLayout(search_group)

        self.role_search = QLineEdit()
        self.role_search.setPlaceholderText("输入角色名、标签或特征...")
        self.role_search.textChanged.connect(self.filter_roles)
        self.role_search.returnPressed.connect(self.search_roles)  # 回车键搜索
        search_layout.addWidget(self.role_search)

        self.search_btn = QPushButton("搜索")
        self.search_btn.setToolTip("搜索角色")
        self.search_btn.clicked.connect(self.search_roles)
        search_layout.addWidget(self.search_btn)

        layout.addWidget(search_group)

        # 角色分类树
        category_group = QGroupBox("角色分类")
        category_layout = QVBoxLayout(category_group)

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.itemClicked.connect(self.on_category_selected)
        category_layout.addWidget(self.category_tree)

        # 分类操作按钮
        category_btn_layout = QHBoxLayout()

        self.add_category_btn = QPushButton("添加分类")
        self.add_category_btn.setToolTip("添加新分类")
        self.add_category_btn.clicked.connect(self.add_category)
        category_btn_layout.addWidget(self.add_category_btn)

        self.edit_category_btn = QPushButton("编辑分类")
        self.edit_category_btn.setToolTip("编辑选中分类")
        self.edit_category_btn.clicked.connect(self.edit_category)
        category_btn_layout.addWidget(self.edit_category_btn)

        self.delete_category_btn = QPushButton("删除分类")
        self.delete_category_btn.setToolTip("删除选中分类")
        self.delete_category_btn.clicked.connect(self.delete_category)
        category_btn_layout.addWidget(self.delete_category_btn)

        category_btn_layout.addStretch()
        category_layout.addLayout(category_btn_layout)

        layout.addWidget(category_group)

        # 角色列表
        list_group = QGroupBox(" 角色列表")
        list_layout = QVBoxLayout(list_group)

        # 角色列表视图（显示详细信息）
        self.role_list = QListWidget()
        self.role_list.setObjectName("RoleListWidget")
        self.role_list.setSelectionMode(QListWidget.SingleSelection)
        self.role_list.itemClicked.connect(self.on_role_item_clicked)
        self.role_list.setStyleSheet("""
            QListWidget#RoleListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget#RoleListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
                margin: 0px;
            }
            QListWidget#RoleListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget#RoleListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 4px solid #1976d2;
            }
        """)
        list_layout.addWidget(self.role_list)

        layout.addWidget(list_group)

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
        basic_group = QGroupBox(" 基本信息")
        basic_layout = QFormLayout(basic_group)

        # 角色名称
        name_layout = QHBoxLayout()
        self.role_name = QLineEdit()
        self.role_name.setPlaceholderText("输入角色名称...")
        self.role_name.textChanged.connect(self.on_basic_info_changed)
        name_layout.addWidget(self.role_name)

        self.role_avatar = QPushButton("头像")
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
        attr_group = QGroupBox(" 角色属性")
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

        parent.addTab(personality_widget, " 性格")

    def create_abilities_tab(self, parent):
        """创建能力标签页"""
        abilities_widget = QWidget()
        layout = QVBoxLayout(abilities_widget)

        # 技能列表
        skills_group = QGroupBox("技能和能力")
        skills_layout = QVBoxLayout(skills_group)

        self.abilities_list = QListWidget()
        self.abilities_list.setMaximumHeight(150)
        skills_layout.addWidget(self.abilities_list)

        # 技能操作按钮
        skill_btn_layout = QHBoxLayout()

        self.add_ability_btn = QPushButton("[+] 添加技能")
        self.add_ability_btn.clicked.connect(self.add_ability)
        skill_btn_layout.addWidget(self.add_ability_btn)

        self.remove_ability_btn = QPushButton("[-] 移除技能")
        self.remove_ability_btn.clicked.connect(self.remove_ability)
        skill_btn_layout.addWidget(self.remove_ability_btn)

        skill_btn_layout.addStretch()
        skills_layout.addLayout(skill_btn_layout)

        layout.addWidget(skills_group)

        # 特殊能力
        special_group = QGroupBox(" 特殊能力")
        special_layout = QVBoxLayout(special_group)

        self.special_abilities = QTextEdit()
        self.special_abilities.setMaximumHeight(100)
        self.special_abilities.setPlaceholderText("描述角色的特殊能力、魔法、超能力等...")
        special_layout.addWidget(self.special_abilities)

        layout.addWidget(special_group)

        # 弱点和限制
        weakness_group = QGroupBox(" 弱点和限制")
        weakness_layout = QVBoxLayout(weakness_group)

        self.weaknesses = QTextEdit()
        self.weaknesses.setMaximumHeight(80)
        self.weaknesses.setPlaceholderText("描述角色的弱点、恐惧、限制等...")
        weakness_layout.addWidget(self.weaknesses)

        layout.addWidget(weakness_group)

        parent.addTab(abilities_widget, " 能力")

    def create_background_info_tab(self, parent):
        """创建背景信息标签页"""
        background_widget = QWidget()
        layout = QVBoxLayout(background_widget)

        # 出身信息
        origin_group = QGroupBox("出身背景")
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
        education_group = QGroupBox("教育经历")
        education_layout = QVBoxLayout(education_group)

        self.education_history = QTextEdit()
        self.education_history.setMaximumHeight(80)
        self.education_history.setPlaceholderText("描述角色的教育背景和重要学习经历...")
        education_layout.addWidget(self.education_history)

        layout.addWidget(education_group)

        parent.addTab(background_widget, "背景")

    def create_relationships_section(self, layout: QVBoxLayout):
        """创建角色关系区域"""
        relation_group = QGroupBox(" 角色关系")
        relation_layout = QVBoxLayout(relation_group)

        # 关系网络视图
        self.relationship_view = QTreeWidget()
        self.relationship_view.setHeaderLabels(["关系", "角色", "描述"])
        relation_layout.addWidget(self.relationship_view)

        # 关系操作按钮
        relation_btn_layout = QHBoxLayout()

        self.add_relation_btn = QPushButton("[+] 添加关系")
        self.add_relation_btn.clicked.connect(self.add_relationship)
        relation_btn_layout.addWidget(self.add_relation_btn)

        self.edit_relation_btn = QPushButton(" 编辑关系")
        self.edit_relation_btn.clicked.connect(self.edit_relationship)
        relation_btn_layout.addWidget(self.edit_relation_btn)

        self.delete_relation_btn = QPushButton(" 删除关系")
        self.delete_relation_btn.clicked.connect(self.delete_relationship)
        relation_btn_layout.addWidget(self.delete_relation_btn)

        relation_btn_layout.addStretch()
        relation_layout.addLayout(relation_btn_layout)

        layout.addWidget(relation_group)

    def create_background_section(self, layout: QVBoxLayout):
        """创建背景故事区域"""
        story_group = QGroupBox("背景故事")
        story_layout = QVBoxLayout(story_group)

        # 背景故事编辑器
        self.background_story = QTextEdit()
        self.background_story.setPlaceholderText("详细描述角色的背景故事、成长经历、重要事件等...")
        story_layout.addWidget(self.background_story)

        # 故事提示
        story_tips = QLabel(" 提示: 可以包含角色的童年经历、重要转折点、性格形成原因等")
        story_tips.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        story_layout.addWidget(story_tips)

        layout.addWidget(story_group)

    def create_bottom_actions(self, layout: QVBoxLayout):
        """创建底部操作栏"""
        action_group = QFrame()
        action_group.setObjectName("RoleActionGroup")
        # 移除硬编码的样式，让主题管理器统一处理
        # 暗色主题的样式已在 theme_manager.py 中统一定义
        action_layout = QHBoxLayout(action_group)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(10)

        # 左侧操作
        self.new_role_btn = QPushButton("[+] 新建角色")
        self.new_role_btn.clicked.connect(self.create_new_role)
        action_layout.addWidget(self.new_role_btn)

        self.save_role_btn = QPushButton(" 保存角色")
        self.save_role_btn.clicked.connect(self.save_current_role)
        action_layout.addWidget(self.save_role_btn)

        self.delete_role_btn = QPushButton(" 删除角色")
        self.delete_role_btn.clicked.connect(self.delete_current_role)
        action_layout.addWidget(self.delete_role_btn)

        action_layout.addWidget(create_separator("vertical"))

        # 中间操作
        self.duplicate_role_btn = QPushButton(" 复制角色")
        self.duplicate_role_btn.clicked.connect(self.duplicate_role)
        action_layout.addWidget(self.duplicate_role_btn)

        self.export_role_btn = QPushButton(" 导出角色")
        self.export_role_btn.clicked.connect(self.export_role)
        action_layout.addWidget(self.export_role_btn)

        self.import_role_btn = QPushButton(" 导入角色")
        self.import_role_btn.clicked.connect(self.import_role)
        action_layout.addWidget(self.import_role_btn)

        action_layout.addWidget(create_separator("vertical"))

        # 模板操作
        self.use_template_btn = QPushButton("使用模板")
        self.use_template_btn.clicked.connect(self.use_role_template)
        action_layout.addWidget(self.use_template_btn)

        self.save_as_template_btn = QPushButton("保存模板")
        self.save_as_template_btn.clicked.connect(self.save_as_template)
        action_layout.addWidget(self.save_as_template_btn)

        action_layout.addStretch()

        # 右侧操作
        self.generate_ai_btn = QPushButton("[AI] 生成角色")
        self.generate_ai_btn.clicked.connect(self.generate_ai_role)
        action_layout.addWidget(self.generate_ai_btn)

        layout.addWidget(action_group)

    def load_sample_data(self):
        """加载示例数据"""
        # 添加分类
        categories = ["全部", "主要角色", "次要角色", "配角", "反派", "路人"]
        for category in categories:
            item = QTreeWidgetItem(self.category_tree, [category])
            item.setIcon(0, QIcon())  # 这里可以添加图标

        # 添加示例角色
        sample_roles = [
            {
                "name": "主角张三",
                "category": "主要角色",
                "type": "主角",
                "gender": "男",
                "age": 25,
                "description": "年轻的修仙者，性格坚毅不拔"
            },
            {
                "name": "导师李四",
                "category": "主要角色",
                "type": "导师",
                "gender": "男",
                "age": 60,
                "description": "资深修仙导师，智慧深邃"
            },
            {
                "name": "反派王五",
                "category": "反派",
                "type": "反派",
                "gender": "男",
                "age": 40,
                "description": "邪恶的反派，企图称霸修仙界"
            },
            {
                "name": "朋友赵六",
                "category": "配角",
                "type": "朋友",
                "gender": "女",
                "age": 23,
                "description": "主角的忠实朋友，聪明机智"
            }
        ]

        # 添加角色到存储和UI
        for role in sample_roles:
            self.add_role(role["name"], role["category"], role)

    def add_role(self, name: str, category: str, role_data: Dict[str, Any] = None):
        """添加角色到存储和UI"""
        if role_data is None:
            role_data = {"name": name, "category": category}

        # 存储到角色列表
        self.all_roles[name] = role_data

        # 检查是否符合当前过滤条件
        if self._role_matches_filter(role_data):
            item = self.create_role_list_item(name, role_data)
            self.role_list.addItem(item)

    def filter_roles(self, text: str):
        """过滤角色（仅支持列表视图）"""
        self.current_filter = text.strip().lower()

        # 刷新列表视图
        self.refresh_role_list()

    def _role_matches_filter(self, role_data: Dict[str, Any]) -> bool:
        """检查角色是否匹配当前过滤条件"""
        # 如果没有过滤文本，默认显示
        if not self.current_filter:
            return self._role_matches_category(role_data)

        # 搜索文本
        search_text = self.current_filter

        # 搜索范围：角色名、描述、类型、性别等
        searchable_fields = [
            role_data.get("name", ""),
            role_data.get("description", ""),
            role_data.get("type", ""),
            role_data.get("gender", ""),
            role_data.get("category", ""),
            role_data.get("personality_description", ""),
            role_data.get("background_story", ""),
            role_data.get("appearance", "")
        ]

        # 检查是否匹配搜索文本
        for field in searchable_fields:
            if search_text in field.lower():
                return self._role_matches_category(role_data)

        return False

    def _role_matches_category(self, role_data: Dict[str, Any]) -> bool:
        """检查角色是否匹配当前分类过滤"""
        if self.current_category == "全部":
            return True

        role_category = role_data.get("category", "未分类")
        return role_category == self.current_category

    def search_roles(self):
        """搜索角色（响应搜索按钮点击或回车键）"""
        search_text = self.role_search.text()
        self.filter_roles(search_text)

    def filter_by_category(self, category: str):
        """按分类过滤"""
        self.current_category = category

        # 重新应用过滤
        self.filter_roles(self.current_filter)

    def on_category_selected(self, item, column):
        """分类选择处理"""
        category_name = item.text(0)
        self.filter_by_category(category_name)

    def on_role_item_clicked(self, item):
        """列表项点击处理"""
        role_name = item.data(Qt.UserRole)
        if not role_name:
            role_name = item.text()

        self.load_role_details(role_name)
        self.current_role = role_name
        self.role_selected.emit(role_name)

    def load_role_details(self, name: str):
        """加载角色详情"""
        self.role_name.setText(name)
        self.role_type.setCurrentText("主角")
        self.role_gender.setCurrentText("男")
        self.role_age.setValue(25)
        self.role_appearance.setPlainText("中等身材，黑色短发，眼神锐利...")
        self.background_story.setPlainText("出生于普通家庭，从小就展现出非凡的能力...")

    def create_new_role(self):
        """创建新角色"""
        self.current_role = ""
        self._safe_clear_editor()

    def _safe_clear_editor(self):
        """安全清空编辑器"""
        self.role_name.blockSignals(True)
        self.role_appearance.blockSignals(True)
        self.personality_description.blockSignals(True)
        self.background_story.blockSignals(True)

        self.role_name.clear()
        self.role_type.setCurrentIndex(0)
        self.role_gender.setCurrentIndex(0)
        self.role_age.setValue(20)
        self.role_appearance.clear()
        self.personality_description.clear()
        self.background_story.clear()

        for checkbox in self.personality_checkboxes.values():
            checkbox.setChecked(False)

        self.role_name.blockSignals(False)
        self.role_appearance.blockSignals(False)
        self.personality_description.blockSignals(False)
        self.background_story.blockSignals(False)

        self.current_role = ""

    def clear_role_list(self):
        """清除角色列表中的所有角色项"""
        self.role_list.clear()

    def refresh_role_list(self):
        """刷新角色列表视图"""
        self.clear_role_list()

        # 添加符合当前过滤条件的角色到列表
        for role_name, role_data in self.all_roles.items():
            if self._role_matches_filter(role_data):
                item = self.create_role_list_item(role_name, role_data)
                self.role_list.addItem(item)

    def create_role_list_item(self, name: str, role_data: Dict[str, Any]) -> QListWidgetItem:
        """创建角色列表项"""
        item = QListWidgetItem()
        item.setText(name)
        item.setData(Qt.UserRole, name)
        item.setSizeHint(self.role_list_item_size())
        return item

    def role_list_item_size(self):
        """设置角色列表项大小"""
        from PySide6.QtCore import QSize
        return QSize(0, 70)

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

    def save_current_role(self):
        """保存当前角色 - 预防性编程"""
        role_data = self.get_role_data()

        # [成功] 预防性验证 - 在保存前就检查所有必要数据
        try:
            role_name = role_data["name"]
            validate_required(role_name, "角色名称")

            # 如果是新角色，设置默认分类
            if "category" not in role_data:
                role_data["category"] = "未分类"

            # 保存到内存中的角色列表
            self.all_roles[role_name] = role_data
            self.current_role = role_name

            # 刷新角色列表
            self.refresh_role_list()

            # 保存到项目文件
            if hasattr(self, 'save_roles'):
                self.save_roles()

            self.role_created.emit(role_name, role_data)
            show_info_dialog(self, "成功", f"角色 '{role_name}' 已保存")

        except ValueError as e:
            # [成功] 输入验证错误
            show_error_dialog(self, "验证失败", str(e))
        except Exception as e:
            # [成功] 文件操作或其他错误
            show_error_dialog(self, "保存失败", f"无法保存角色: {str(e)}")

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
            # 从 all_roles 中删除角色
            if self.current_role in self.all_roles:
                del self.all_roles[self.current_role]
                # 保存更新后的角色列表
                if hasattr(self, 'save_roles'):
                    self.save_roles()

            self.role_deleted.emit(self.current_role)

            # 刷新角色列表
            self.refresh_role_list()

            # 清空编辑器
            self.clear_editor()

            show_info_dialog(self, "成功", f"角色 '{self.current_role}' 已删除")

    def clear_editor(self):
        """清空编辑器"""
        self.current_role = ""  # 重置当前角色

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

        try:
            # 获取当前角色数据
            if self.current_role not in self.all_roles:
                show_error_dialog(self, "错误", "未找到当前角色数据")
                return

            original_role = self.all_roles[self.current_role].copy()

            # 生成新的角色名
            new_name = f"{self.current_role}(副本)"
            counter = 1
            while new_name in self.all_roles:
                new_name = f"{self.current_role}(副本{counter})"
                counter += 1

            # 更新新角色数据
            original_role["name"] = new_name
            original_role["category"] = original_role.get("category", "未分类")

            # 添加到角色列表
            self.add_role(new_name, original_role["category"], original_role)

            # 保存到项目
            if hasattr(self, 'save_roles'):
                self.save_roles()

            show_info_dialog(self, "成功", f"角色 '{self.current_role}' 已复制为 '{new_name}'")

        except Exception as e:
            show_error_dialog(self, "错误", f"复制角色失败:\n{str(e)}")

    def export_role(self):
        """导出角色"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        import os

        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出角色",
                f"role_{self.current_role if self.current_role else 'all'}.json",
                "JSON文件 (*.json);;所有文件 (*)"
            )

            if not file_path:
                return

            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 准备导出数据
            export_data = {}

            if self.current_role:
                # 导出当前选中的角色
                if self.current_role in self.all_roles:
                    export_data[self.current_role] = self.all_roles[self.current_role]
                else:
                    show_error_dialog(self, "错误", "未找到当前角色数据")
                    return
            else:
                # 导出所有角色
                export_data = self.all_roles

            # 添加导出元信息
            export_metadata = {
                "export_time": str(os.path.getmtime(file_path) if os.path.exists(file_path) else ""),
                "role_count": len(export_data),
                "version": "1.0"
            }

            # 创建最终导出数据
            final_data = {
                "metadata": export_metadata,
                "roles": export_data
            }

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)

            file_name = os.path.basename(file_path)
            show_info_dialog(
                self,
                "成功",
                f"角色导出成功！\n\n"
                f"文件: {file_name}\n"
                f"角色数量: {len(export_data)}\n"
                f"保存位置: {file_path}"
            )

        except Exception as e:
            show_error_dialog(self, "错误", f"导出角色失败:\n{str(e)}")

    def import_role(self):
        """导入角色"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        import os

        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "导入角色",
                "",
                "JSON文件 (*.json);;所有文件 (*)"
            )

            if not file_path:
                return

            # 检查文件是否存在
            if not os.path.exists(file_path):
                show_error_dialog(self, "错误", "选择的文件不存在")
                return

            # 读取并解析JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 处理不同的数据格式
            roles_to_import = {}

            if "metadata" in data and "roles" in data:
                # 格式1: 包含元信息
                roles_to_import = data["roles"]
            elif isinstance(data, dict) and any(k for k in data.keys() if k != "metadata"):
                # 格式2: 直接是角色字典
                roles_to_import = data
            else:
                show_error_dialog(self, "错误", "无效的角色数据格式")
                return

            if not roles_to_import:
                show_error_dialog(self, "错误", "文件中没有找到角色数据")
                return

            # 处理重复的角色名
            imported_count = 0
            skipped_count = 0
            for role_name, role_data in roles_to_import.items():
                # 检查角色名是否已存在
                if role_name in self.all_roles:
                    # 生成新名称
                    new_name = f"{role_name}(导入)"
                    counter = 1
                    while new_name in self.all_roles:
                        new_name = f"{role_name}(导入{counter})"
                        counter += 1

                    # 更新角色名
                    role_data["name"] = new_name
                    self.add_role(new_name, role_data.get("category", "未分类"), role_data)
                    imported_count += 1
                else:
                    # 直接添加
                    self.add_role(role_name, role_data.get("category", "未分类"), role_data)
                    imported_count += 1

            # 保存到项目
            if hasattr(self, 'save_roles'):
                self.save_roles()

            file_name = os.path.basename(file_path)
            show_info_dialog(
                self,
                "成功",
                f"角色导入完成！\n\n"
                f"文件: {file_name}\n"
                f"成功导入: {imported_count} 个角色\n"
                f"跳过: {skipped_count} 个角色\n"
                f"总角色数: {len(self.all_roles)}"
            )

        except json.JSONDecodeError as e:
            show_error_dialog(self, "错误", f"JSON格式错误:\n{str(e)}")
        except Exception as e:
            show_error_dialog(self, "错误", f"导入角色失败:\n{str(e)}")

    def generate_ai_role(self):
        """AI生成角色"""
        # 这里实现AI生成逻辑
        show_info_dialog(self, "提示", "AI角色生成功能待实现")

    def add_category(self):
        """添加分类"""
        from PySide6.QtWidgets import QInputDialog

        # 弹出输入对话框
        category_name, ok = QInputDialog.getText(
            self, "添加分类", "请输入新分类名称:", text=""
        )

        if ok and category_name.strip():
            category_name = category_name.strip()

            # 检查分类是否已存在
            existing_items = []
            for i in range(self.category_tree.topLevelItemCount()):
                item = self.category_tree.topLevelItem(i)
                existing_items.append(item.text(0))

            if category_name in existing_items:
                show_error_dialog(self, "错误", f"分类 '{category_name}' 已存在！")
                return

            # 添加新分类
            new_item = QTreeWidgetItem(self.category_tree, [category_name])
            self.category_tree.addTopLevelItem(new_item)
            self.category_tree.setCurrentItem(new_item)

            show_info_dialog(self, "成功", f"分类 '{category_name}' 添加成功！")

        elif ok and not category_name.strip():
            show_error_dialog(self, "错误", "分类名称不能为空！")

    def edit_category(self):
        """编辑分类"""
        from PySide6.QtWidgets import QInputDialog

        # 获取当前选中的分类
        current_item = self.category_tree.currentItem()

        if not current_item:
            show_error_dialog(self, "错误", "请先选择要编辑的分类！")
            return

        # 获取当前分类名称
        old_name = current_item.text(0)

        # 弹出输入对话框，预填当前名称
        new_name, ok = QInputDialog.getText(
            self, "编辑分类", "请输入新分类名称:", text=old_name
        )

        if ok and new_name.strip():
            new_name = new_name.strip()

            # 检查新名称是否与其他分类重名
            for i in range(self.category_tree.topLevelItemCount()):
                item = self.category_tree.topLevelItem(i)
                if item != current_item and item.text(0) == new_name:
                    show_error_dialog(self, "错误", f"分类 '{new_name}' 已存在！")
                    return

            # 更新分类名称
            current_item.setText(0, new_name)
            show_info_dialog(self, "成功", f"分类 '{old_name}' 已更名为 '{new_name}'")

        elif ok and not new_name.strip():
            show_error_dialog(self, "错误", "分类名称不能为空！")

    def delete_category(self):
        """删除分类"""
        from PySide6.QtWidgets import QMessageBox

        # 获取当前选中的分类
        current_item = self.category_tree.currentItem()

        if not current_item:
            show_error_dialog(self, "错误", "请先选择要删除的分类！")
            return

        category_name = current_item.text(0)

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除分类 '{category_name}' 吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 删除分类
            index = self.category_tree.indexOfTopLevelItem(current_item)
            self.category_tree.takeTopLevelItem(index)

            show_info_dialog(self, "成功", f"分类 '{category_name}' 已删除")

            # 如果删除后还有分类，选中第一个
            if self.category_tree.topLevelItemCount() > 0:
                first_item = self.category_tree.topLevelItem(0)
                self.category_tree.setCurrentItem(first_item)
                self.on_category_selected(first_item, 0)

    def add_ability(self):
        """添加技能"""
        from PySide6.QtWidgets import QInputDialog, QMessageBox

        # 弹出输入对话框
        ability_name, ok = QInputDialog.getText(
            self, "添加技能", "请输入技能名称:", text=""
        )

        if ok and ability_name.strip():
            ability_name = ability_name.strip()

            # 检查技能是否已存在
            existing_items = []
            for i in range(self.abilities_list.count()):
                existing_items.append(self.abilities_list.item(i).text())

            if ability_name in existing_items:
                show_error_dialog(self, "错误", f"技能 '{ability_name}' 已存在！")
                return

            # 添加技能到列表
            self.abilities_list.addItem(ability_name)
            self.abilities_list.setCurrentRow(self.abilities_list.count() - 1)

            show_info_dialog(self, "成功", f"技能 '{ability_name}' 添加成功！")

        elif ok and not ability_name.strip():
            show_error_dialog(self, "错误", "技能名称不能为空！")

    def remove_ability(self):
        """移除技能"""
        from PySide6.QtWidgets import QMessageBox

        # 获取当前选中的技能
        current_item = self.abilities_list.currentItem()

        if not current_item:
            show_error_dialog(self, "错误", "请先选择要删除的技能！")
            return

        ability_name = current_item.text()

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除技能 '{ability_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 删除技能
            row = self.abilities_list.row(current_item)
            self.abilities_list.takeItem(row)

            show_info_dialog(self, "成功", f"技能 '{ability_name}' 已删除")

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
        from PySide6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PySide6.QtGui import QPixmap, QIcon
        from PySide6.QtCore import Qt
        import os
        import shutil

        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择角色头像",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.ico);;所有文件 (*)"
        )

        if not file_path:
            return  # 用户取消选择

        # 检查文件是否存在
        if not os.path.exists(file_path):
            show_error_dialog(self, "错误", "选择的文件不存在")
            return

        # 验证图片文件
        try:
            # 尝试加载图片以验证格式
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                show_error_dialog(self, "错误", "无法加载图片文件，请检查文件格式")
                return
        except Exception as e:
            show_error_dialog(self, "错误", f"图片验证失败: {str(e)}")
            return

        # 如果有当前角色，将头像保存到角色数据
        if self.current_role and self.current_role in self.all_roles:
            # 创建头像存储目录
            avatars_dir = os.path.join(os.path.dirname(self.current_project_path) if self.current_project_path else "/tmp", "avatars")
            if not os.path.exists(avatars_dir):
                os.makedirs(avatars_dir, exist_ok=True)

            # 复制头像到项目目录
            avatar_filename = f"{self.current_role}.png"
            avatar_path = os.path.join(avatars_dir, avatar_filename)

            try:
                # 调整头像大小（如果需要）
                scaled_pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                scaled_pixmap.save(avatar_path, "PNG")

                # 更新角色数据
                self.all_roles[self.current_role]["avatar_path"] = avatar_path

                show_info_dialog(self, "成功", f"角色头像已设置！\n保存位置: {avatar_path}")

            except Exception as e:
                show_error_dialog(self, "错误", f"保存头像失败: {str(e)}")
        else:
            # 没有当前角色，显示头像预览
            self.show_avatar_preview(file_path)

    def show_avatar_preview(self, file_path: str):
        """显示头像预览对话框"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("头像预览")
        dialog.setModal(True)
        dialog.resize(300, 350)

        layout = QVBoxLayout(dialog)

        # 显示图片
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # 缩放图片
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            avatar_label = QLabel()
            avatar_label.setPixmap(scaled_pixmap)
            avatar_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(avatar_label)

        # 文件信息
        import os
        file_info = QLabel(f"文件名: {os.path.basename(file_path)}")
        file_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(file_info)

        file_size = os.path.getsize(file_path) / 1024  # KB
        size_label = QLabel(f"大小: {file_size:.1f} KB")
        size_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(size_label)

        # 按钮
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.exec()

    def load_project(self, project_path: str):
        """加载项目"""
        self.current_project_path = project_path

        # 初始化数据管理器
        if not self.data_manager:
            self.data_manager = DataManager(project_path)

        # 尝试加载已保存的角色数据
        try:
            if hasattr(self.data_manager, 'load_roles'):
                roles_data = self.data_manager.load_roles()
                if roles_data:
                    # 清除现有角色
                    self.clear_all_roles()

                    # 加载保存的角色
                    for role_name, role_data in roles_data.items():
                        self.add_role(role_name, role_data.get("category", "未分类"), role_data)
        except Exception as e:
            # 如果没有保存的角色数据或加载失败，使用示例数据
            print(f"加载角色数据失败: {e}")

    def clear_all_roles(self):
        """清除所有角色"""
        self.all_roles.clear()
        self.clear_role_list()

    def save_roles(self):
        """保存角色数据到项目"""
        if self.data_manager and hasattr(self.data_manager, 'save_roles'):
            try:
                self.data_manager.save_roles(self.all_roles)
            except Exception as e:
                show_error_dialog(self, "错误", f"保存角色失败:\n{str(e)}")
    # ========== 角色模板系统 ==========

    def use_role_template(self):
        """使用角色模板"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QScrollArea, QFrame
        from PySide6.QtCore import Qt
        
        # 创建模板选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择角色模板")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("请选择角色模板:"))
        
        # 模板网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        template_widget = QWidget()
        template_grid = QGridLayout(template_widget)
        template_grid.setSpacing(10)
        
        # 预设模板
        templates = [
            ("主角模板", "适用于小说的主要角色，通常有完整的成长弧线"),
            ("导师模板", "适用于指导主角的智者或长者角色"),
            ("反派模板", "适用于主要反派或对立角色"),
            ("朋友模板", "适用于主角的挚友或支持者"),
            ("恋人模板", "适用于爱情线角色"),
            ("配角模板", "适用于功能性配角"),
            ("路人模板", "适用于龙套或背景角色"),
            ("神秘模板", "适用于身份不明的神秘角色"),
        ]
        
        for i, (name, desc) in enumerate(templates):
            btn = QPushButton(f"{name}\n{desc}")
            btn.setMinimumHeight(60)
            btn.clicked.connect(lambda checked, t=name: self.apply_template(t, dialog))
            template_grid.addWidget(btn, i // 2, i % 2)
        
        scroll.setWidget(template_widget)
        layout.addWidget(scroll)
        
        # 按钮
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def apply_template(self, template_name: str, dialog: QDialog):
        """应用模板"""
        templates_data = {
            "主角模板": {
                "name": "新主角",
                "category": "主要角色",
                "age": "20-30岁",
                "description": "一个有着远大理想的年轻人，虽然经历挫折但始终坚持自己的信念...",
                "personality": ["勇敢", "坚定", "乐观", "有领导力"],
                "background": "出身平凡家庭，通过自己的努力逐渐成长..."
            },
            "导师模板": {
                "name": "导师",
                "category": "主要角色",
                "age": "50-70岁",
                "description": "经验丰富、智慧深邃的长者，默默指导着年轻人...",
                "personality": ["智慧", "沉稳", "慈祥", "洞察力强"],
                "background": "有着丰富的阅历和深刻的见解..."
            },
            "反派模板": {
                "name": "反派",
                "category": "反派",
                "age": "40-50岁",
                "description": "表面道貌岸然，内心却有着扭曲的欲望和野心...",
                "personality": ["狡猾", "自私", "有魅力", "冷酷"],
                "background": "曾经也是正义之士，但因某些经历而走向黑暗..."
            },
            "朋友模板": {
                "name": "朋友",
                "category": "配角",
                "age": "20-30岁",
                "description": "主角的挚友，总是在关键时刻提供帮助和支持...",
                "personality": ["忠诚", "幽默", "可靠", "善良"],
                "background": "与主角有着深厚的友谊..."
            },
            "恋人模板": {
                "name": "恋人",
                "category": "主要角色",
                "age": "20-30岁",
                "description": "与主角有着复杂感情纠葛的人...",
                "personality": ["温柔", "独立", "坚强", "敏感"],
                "background": "有着自己的理想和追求..."
            },
            "配角模板": {
                "name": "配角",
                "category": "配角",
                "age": "30-40岁",
                "description": "在故事中发挥特定功能性的角色...",
                "personality": ["专业", "负责", "配合度高"],
                "background": "在自己的领域有着专业技能..."
            },
            "路人模板": {
                "name": "路人",
                "category": "路人",
                "age": "20-60岁",
                "description": "不起眼的小角色，偶尔出现推动剧情...",
                "personality": ["普通", "善良"],
                "background": "过着平凡的生活..."
            },
            "神秘模板": {
                "name": "神秘人物",
                "category": "路人",
                "age": "未知",
                "description": "身份成谜，行为诡秘，让人捉摸不透...",
                "personality": ["神秘", "不可预测", "深沉"],
                "background": "过去成谜，动机不明..."
            }
        }
        
        data = templates_data.get(template_name, {})
        
        # 清空当前角色
        self.create_new_role()
        
        # 应用模板
        if data:
            self.role_name.setText(data.get("name", ""))
            self.role_age.setText(data.get("age", ""))
            self.role_description.setPlainText(data.get("description", ""))
            self.personality_description.setPlainText(data.get("background", ""))
        
        dialog.accept()
        show_info_dialog(self, "成功", f"已应用模板: {template_name}")

    def save_as_template(self):
        """保存当前角色为模板"""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        
        name, ok = QInputDialog.getText(
            self, "保存模板", 
            "请输入模板名称:"
        )
        
        if ok and name:
            # 这里可以实现保存逻辑
            show_info_dialog(self, "成功", f"已保存模板: {name}")

    def generate_ai_role(self):
        """AI辅助角色创建"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QTextEdit, QLineEdit, QGroupBox
        from PySide6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("[AI] AI角色生成器")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)

        # 描述输入
        input_group = QGroupBox("角色信息输入")
        input_layout = QFormLayout(input_group)

        self.role_desc_input = QLineEdit()
        self.role_desc_input.setPlaceholderText("请输入你想要创建的角色描述，如：年轻的魔法师，性格内向但天赋异禀...")
        input_layout.addRow("角色描述:", self.role_desc_input)

        self.additional_notes_input = QTextEdit()
        self.additional_notes_input.setPlaceholderText("可以补充更多细节，如背景、目标等...")
        self.additional_notes_input.setMaximumHeight(100)
        input_layout.addRow("补充说明:", self.additional_notes_input)

        layout.addWidget(input_group)

        # 提示信息
        from PySide6.QtWidgets import QLabel
        tip_label = QLabel("提示：角色描述越详细，生成的角色越精准。建议包含角色的职业、性格、目标等信息。")
        tip_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(tip_label)

        # 按钮
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        generate_btn = QPushButton("生成角色")
        generate_btn.setObjectName("GenerateRoleButton")
        generate_btn.setProperty("style", "primary")
        generate_btn.clicked.connect(lambda: self._perform_ai_generation_with_inputs(dialog))
        btn_layout.addWidget(generate_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _perform_ai_generation_with_inputs(self, dialog: QDialog):
        """执行AI生成 - 带有输入参数"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 获取用户输入
            role_description = self.role_desc_input.text().strip()
            additional_notes = self.additional_notes_input.toPlainText().strip()

            # 如果没有输入，使用默认值
            if not role_description:
                role_description = "一个充满神秘感的角色"

            if not additional_notes:
                additional_notes = "无特殊要求"

            logger.info(f"开始AI角色生成，描述: {role_description[:50]}...")

            # 获取当前LLM配置
            if "choose_configs" in self.config and "architecture_llm" in self.config["choose_configs"]:
                selected_llm_name = self.config["choose_configs"]["architecture_llm"]
            elif "last_interface_format" in self.config:
                # 如果没有选择配置，使用默认配置
                if "llm_configs" in self.config and self.config["llm_configs"]:
                    # 尝试找到匹配last_interface_format的配置
                    found = False
                    for name, config in self.config["llm_configs"].items():
                        if config.get("interface_format", "").lower() == self.config["last_interface_format"].lower():
                            selected_llm_name = name
                            found = True
                            break
                    if not found:
                        selected_llm_name = list(self.config["llm_configs"].keys())[0]
                else:
                    show_error_dialog(self, "错误", "未找到可用的LLM配置，请先在配置管理中设置LLM")
                    dialog.accept()
                    return
            else:
                # 使用第一个可用的配置
                if "llm_configs" in self.config and self.config["llm_configs"]:
                    selected_llm_name = list(self.config["llm_configs"].keys())[0]
                else:
                    show_error_dialog(self, "错误", "未找到可用的LLM配置，请先在配置管理中设置LLM")
                    dialog.accept()
                    return

            # 获取LLM配置详情
            if "llm_configs" not in self.config or selected_llm_name not in self.config["llm_configs"]:
                show_error_dialog(self, "错误", f"LLM配置 '{selected_llm_name}' 不存在，请检查配置")
                dialog.accept()
                return

            llm_config = self.config["llm_configs"][selected_llm_name]

            # 验证配置
            if not llm_config.get("api_key"):
                show_error_dialog(self, "错误", f"LLM配置 '{selected_llm_name}' 缺少API密钥")
                dialog.accept()
                return

            logger.info(f"使用LLM配置: {selected_llm_name}, 接口: {llm_config.get('interface_format')}")

            # 创建LLM适配器
            from llm_adapters import create_llm_adapter
            from prompt_definitions import ai_role_generation_prompt

            # 构建提示词
            prompt = ai_role_generation_prompt.format(
                role_description=role_description,
                additional_notes=additional_notes
            )

            logger.debug(f"提示词长度: {len(prompt)} 字符")

            # 创建适配器
            llm_adapter = create_llm_adapter(
                interface_format=llm_config.get("interface_format", "OpenAI"),
                base_url=llm_config.get("base_url", ""),
                model_name=llm_config.get("model_name", ""),
                api_key=llm_config.get("api_key", ""),
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 8192),
                timeout=llm_config.get("timeout", 600)
            )

            # 调用LLM生成角色
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import QTimer
            import json
            import re
            import threading

            # 显示进度对话框
            progress = QProgressDialog("正在生成角色...", "取消", 0, 0, dialog)
            progress.setWindowTitle("AI生成中")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            def generate_role():
                import time
                import threading

                # 设置超时时间（60秒）
                timeout = 60
                start_time = time.time()

                try:
                    logger.info("开始调用LLM API...")
                    logger.info(f"设置超时时间: {timeout}秒")

                    # 调用LLM
                    response = llm_adapter.invoke(prompt)

                    # 检查是否超时
                    elapsed = time.time() - start_time
                    logger.info(f"API调用耗时: {elapsed:.2f}秒")
                    logger.info(f"LLM响应长度: {len(response) if response else 0} 字符")

                    # 记录前200个字符作为调试信息
                    if response:
                        logger.debug(f"LLM响应前200字符: {response[:200]}")
                    else:
                        logger.warning("LLM返回空响应")

                    if elapsed > timeout:
                        progress.close()
                        dialog.accept()
                        error_msg = f"API调用超时（>{timeout}秒），请检查网络连接或增加超时时间"
                        logger.error(error_msg)
                        show_error_dialog(self, "生成失败", error_msg)
                        return

                    if not response:
                        progress.close()
                        dialog.accept()
                        error_msg = "未获取到LLM响应，请检查网络连接和API配置"
                        logger.error(error_msg)
                        show_error_dialog(self, "生成失败", error_msg)
                        return

                    # 解析JSON响应
                    # 尝试提取JSON部分
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        logger.info(f"找到JSON片段，长度: {len(json_str)}")
                        try:
                            role_data = json.loads(json_str)
                            logger.info(f"成功解析JSON，角色名: {role_data.get('name', '未知')}")
                            logger.info("存储角色数据并通知主线程...")

                            # 使用线程安全的方式存储数据
                            with self.pending_role_data_lock:
                                self.pending_role_data = {
                                    'role_data': role_data,
                                    'progress': progress,
                                    'dialog': dialog
                                }

                            # [成功] 角色数据已安全存储，主线程定时器将自动轮询
                            logger.info("[成功] 角色数据已安全存储到pending_role_data")
                            logger.info("[成功] 主线程的轮询定时器将自动检测并处理")

                        except json.JSONDecodeError as e:
                            progress.close()
                            dialog.accept()
                            error_msg = f"LLM返回的数据格式不正确，无法解析: {str(e)}"
                            logger.error(f"{error_msg}\n原始响应: {response[:500]}")
                            show_error_dialog(self, "解析错误", error_msg)
                    else:
                        progress.close()
                        dialog.accept()
                        error_msg = "未找到有效的JSON数据"
                        logger.error(f"{error_msg}\n原始响应: {response[:500]}")
                        show_error_dialog(self, "解析错误", error_msg)

                except Exception as e:
                    progress.close()
                    dialog.accept()
                    error_msg = f"生成角色时出错: {str(e)}"
                    logger.error(f"{error_msg}\n异常类型: {type(e).__name__}")
                    import traceback
                    logger.error(traceback.format_exc())
                    show_error_dialog(self, "错误", error_msg)

            # 在新线程中执行生成
            thread = threading.Thread(target=generate_role, daemon=True)
            thread.start()

        except Exception as e:
            dialog.accept()
            error_msg = f"AI生成功能出错: {str(e)}"
            logger.error(f"{error_msg}\n异常类型: {type(e).__name__}")
            import traceback
            logger.error(traceback.format_exc())
            show_error_dialog(self, "错误", error_msg)

    def _check_pending_role_data(self):
        """检查并处理待处理的角色数据（主线程中执行）"""
        import logging
        import traceback

        logger = logging.getLogger(__name__)
        logger.info("[定时器] 检查待处理的角色数据...")

        # 获取待处理数据
        with self.pending_role_data_lock:
            if not self.pending_role_data:
                return  # 没有数据就继续轮询，不输出日志避免刷屏

            data = self.pending_role_data.copy()
            self.pending_role_data = None

        try:
            role_data = data['role_data']
            progress = data['progress']
            dialog = data['dialog']

            logger.info(f"[定时器] 开始应用生成的角色数据到UI...")
            logger.info(f"[定时器] 角色名: {role_data.get('name', '未知')}")

            # 关闭进度对话框
            logger.info("[定时器] 关闭进度对话框...")
            try:
                progress.close()
            except Exception as e:
                logger.warning(f"关闭进度对话框失败: {e}")

            # 清空当前角色
            logger.info("[定时器] 清空当前角色编辑器...")
            self._safe_clear_editor()

            # 设置基本信息
            logger.info("[定时器] 设置角色基本信息...")
            try:
                if "name" in role_data:
                    logger.info(f"  - 角色名: {role_data['name']}")
                    self.role_name.setText(role_data["name"])
                if "type" in role_data:
                    logger.info(f"  - 角色类型: {role_data['type']}")
                    self.role_type.setCurrentText(role_data["type"])
                if "gender" in role_data:
                    logger.info(f"  - 性别: {role_data['gender']}")
                    self.role_gender.setCurrentText(role_data["gender"])
                if "age" in role_data:
                    logger.info(f"  - 年龄: {role_data['age']}")
                    self.role_age.setValue(int(role_data["age"]))
            except Exception as e:
                logger.error(f"[定时器] 设置基本信息时出错: {e}")
                logger.error(traceback.format_exc())

            # 设置详细描述
            logger.info("[定时器] 设置详细描述...")
            try:
                if "appearance" in role_data:
                    appearance_preview = role_data["appearance"][:50] + "..." if len(role_data["appearance"]) > 50 else role_data["appearance"]
                    logger.info(f"  - 外貌: {appearance_preview}")
                    self.role_appearance.setPlainText(role_data["appearance"])
                if "personality_description" in role_data:
                    personality_preview = role_data["personality_description"][:50] + "..." if len(role_data["personality_description"]) > 50 else role_data["personality_description"]
                    logger.info(f"  - 性格: {personality_preview}")
                    self.personality_description.setPlainText(role_data["personality_description"])
                if "background_story" in role_data:
                    background_preview = role_data["background_story"][:50] + "..." if len(role_data["background_story"]) > 50 else role_data["background_story"]
                    logger.info(f"  - 背景: {background_preview}")
                    self.background_story.setPlainText(role_data["background_story"])
            except Exception as e:
                logger.error(f"[定时器] 设置详细描述时出错: {e}")
                logger.error(traceback.format_exc())

            # 设置性格特质
            logger.info("[定时器] 设置性格特质...")
            try:
                if "personalities" in role_data:
                    personalities = role_data["personalities"]
                    logger.info(f"  - 性格列表: {personalities}")
                    for trait, checkbox in self.personality_checkboxes.items():
                        if trait in personalities:
                            logger.info(f"    ✓ {trait}")
                            checkbox.setChecked(True)
            except Exception as e:
                logger.error(f"[定时器] 设置性格特质时出错: {e}")
                logger.error(traceback.format_exc())

            # 关闭生成对话框
            logger.info("[定时器] 关闭生成对话框...")
            try:
                dialog.accept()
                logger.info("[定时器] 对话框已关闭")
            except Exception as e:
                logger.warning(f"关闭对话框失败: {e}")

            # 显示成功提示
            logger.info("[定时器] 显示状态栏提示...")
            try:
                from PySide6.QtWidgets import QApplication

                app = QApplication.instance()
                if app and hasattr(app, 'main_window') and hasattr(app.main_window, 'statusBar'):
                    status_bar = app.main_window.statusBar()
                    role_name = role_data.get('name', '未知')
                    status_bar.showMessage(f"[成功] 角色 '{role_name}' 生成成功！", 5000)
                    logger.info(f"[定时器] 状态栏提示已显示: 角色 '{role_name}' 生成成功")
                else:
                    logger.warning("[定时器] 无法访问状态栏")
            except Exception as e:
                logger.error(f"[定时器] 状态栏提示失败: {e}")

            logger.info("[定时器] 角色应用完成！")

        except Exception as e:
            logger.error(f"[定时器] 处理待处理数据时出错: {e}")
            logger.error(traceback.format_exc())

    def _safe_clear_editor(self):
        """安全清空编辑器（避免在异步操作中调用setFocus）"""
        try:
            self.role_name.blockSignals(True)
            self.role_appearance.blockSignals(True)
            self.personality_description.blockSignals(True)
            self.background_story.blockSignals(True)

            self.role_name.clear()
            self.role_type.setCurrentIndex(0)
            self.role_gender.setCurrentIndex(0)
            self.role_age.setValue(20)
            self.role_appearance.clear()
            self.personality_description.clear()
            self.background_story.clear()

            for checkbox in self.personality_checkboxes.values():
                checkbox.setChecked(False)

        finally:
            self.role_name.blockSignals(False)
            self.role_appearance.blockSignals(False)
            self.personality_description.blockSignals(False)
            self.background_story.blockSignals(False)

        self.current_role = ""

    def _show_success_and_close(self, role_data: dict, dialog: QDialog):
        """显示成功提示并关闭对话框"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            dialog.accept()
            logger.info("生成对话框已关闭")

            # 使用非阻塞的提示
            show_info_dialog(self, "[成功] 成功", f"角色 '{role_data.get('name', '未知')}' 已生成！\n请查看右侧编辑器中的详细信息。")
            logger.info("角色生成完成！")

        except Exception as e:
            logger.error(f"显示成功提示时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
