# InfiniteQuill - 架构决策文档

**项目**: InfiniteQuill - AI驱动的智能小说创作平台
**文档类型**: 决策架构与实现指导
**创建日期**: 2025-11-18
**目标**: 指导AI代理实施完整的48个功能需求和6个Epic

---

## 📊 执行摘要

本文档为InfiniteQuill项目提供完整的架构决策和实现指导，基于6个关键架构决策，构建了一个分层、模块化、可扩展的技术架构。

**核心架构特点：**
- **混合数据管理** - SQLite + 文件系统 + ChromaDB
- **分层组件架构** - 基础层→功能层→界面层
- **适配器模式** - 统一的LLM和嵌入服务接口
- **向量检索增强** - 基于现有ChromaDB实现的语义搜索
- **主题统一管理** - Material Design浅色/深色主题系统

---

## 🎯 架构决策矩阵

| 决策领域 | 选择方案 | 技术实现 | 影响Epic | 核心优势 |
|---------|---------|---------|---------|---------|
| **角色管理数据模型** | 混合设计 | SQLite基础表 + JSON详情文档 | Epic 2、3、5 | 平衡性能与灵活性 |
| **AI生成流程架构** | 分层架构 | 四层架构：交互层→业务层→服务层→数据层 | Epic 3、4、6 | 职责清晰易扩展 |
| **多LLM适配器设计** | 适配器模式 | 统一BaseLLMAdapter接口 + 管理器模式 | Epic 4、6 | 统一接口易扩展 |
| **向量检索策略** | 基础向量检索 | 现有ChromaDB + 多适配器 + 智能过滤 | Epic 3、6 | 成熟稳定，利用现有API |
| **UI组件架构** | 分层组件架构 | ThemedWidget → Controller → UI组装 | Epic 5、6 | 职责分离，主题统一 |
| **数据持久化策略** | 混合存储策略 | SQLite结构化 + 文件大内容 + ChromaDB向量 | Epic 1、2、3、6 | 发挥优势，保持兼容 |

---

## 🏗️ 完整项目架构

### 📁 目录结构设计

```
InfiniteQuill/
├── main.py                          # 应用入口点
├── config_manager.py                 # 配置管理（增强自动保存）
├── project_manager.py                # 项目管理（混合存储支持）
│
├── ui_qt/                           # UI分层架构
│   ├── main_window.py               # 主窗口（主题化）
│   ├── theme_manager.py             # 主题管理器
│   ├── widgets/                     # 基础组件层
│   │   ├── themed_widget.py         # 主题化基础组件
│   │   ├── searchable_list.py       # 可搜索列表组件
│   │   ├── character_detail.py      # 角色详情组件
│   │   ├── character_approval.py    # 角色审批组件
│   │   ├── chapter_editor.py        # 富文本章节编辑器
│   │   └── config_widget.py         # 配置管理组件
│   └── styles/                      # 主题样式文件
│       ├── material_light.qss       # 浅色主题
│       └── material_dark.qss        # 深色主题
│
├── controllers/                     # 业务逻辑层
│   ├── character_controller.py      # 角色管理业务逻辑
│   ├── generation_controller.py     # AI生成业务逻辑
│   ├── project_controller.py        # 项目管理业务逻辑
│   └── theme_controller.py          # 主题控制逻辑
│
├── services/                        # 服务层
│   ├── llm_service.py               # LLM服务管理
│   ├── embedding_service.py         # 嵌入服务管理
│   ├── character_service.py          # 角色数据服务
│   ├── generation_service.py        # 生成服务
│   └── theme_service.py             # 主题服务
│
├── data/                           # 数据访问层
│   ├── database_manager.py          # SQLite数据库管理
│   ├── file_storage_manager.py      # 文件存储管理
│   ├── hybrid_data_manager.py       # 混合数据管理器
│   └── vector_manager.py            # 向量存储管理
│
├── novel_generator/                 # AI生成核心（保持现有）
│   ├── architecture.py              # 世界观生成
│   ├── blueprint.py                 # 章节蓝图生成
│   ├── chapter.py                   # 章节内容生成
│   ├── knowledge.py                 # 知识库管理
│   ├── vectorstore_utils.py         # 向量存储工具
│   └── consistency_checker.py       # 一致性检查
│
├── adapters/                        # 适配器层
│   ├── base_llm_adapter.py          # LLM适配器基类
│   ├── base_embedding_adapter.py    # 嵌入适配器基类
│   ├── llm_adapters.py              # LLM适配器实现（现有）
│   └── embedding_adapters.py        # 嵌入适配器实现（现有）
│
├── models/                          # 数据模型
│   ├── character_model.py           # 角色数据模型
│   ├── project_model.py             # 项目数据模型
│   ├── generation_model.py          # 生成数据模型
│   └── base_model.py                # 基础数据模型
│
├── utils/                           # 工具函数
│   ├── naming_patterns.py           # 命名模式定义
│   ├── data_formats.py              # 数据格式定义
│   ├── event_patterns.py            # 事件模式定义
│   └── validation_utils.py          # 验证工具
│
└── tests/                           # 测试代码
    ├── unit/                        # 单元测试
    ├── integration/                 # 集成测试
    └── ui/                          # UI测试
```

---

## 🎯 Epic到架构映射

### Epic 1: 项目管理基础设施
**架构组件：**
- **HybridDataManager** - 混合数据管理器
- **ProjectController** - 项目业务逻辑
- **SQLiteManager** - 项目数据持久化
- **ConfigWidget** - 配置管理界面

**关键实现：**
```python
# 项目创建流程
project_controller = ProjectController(data_manager)
project_id = project_controller.create_project({
    'name': '新小说项目',
    'genre': '科幻',
    'config': user_config
})
```

### Epic 2: 核心差异化功能 - 角色管理
**架构组件：**
- **CharacterController** - 角色业务逻辑
- **CharacterModel** - 角色数据模型
- **CharacterApprovalWidget** - 角色审批界面
- **AI服务集成** - 角色提案生成

**关键实现：**
```python
# 角色创建和审批流程
character_controller = CharacterController(llm_service, character_service)

# 1. AI生成提案
proposals = character_controller.generate_character_proposals(description)

# 2. 用户审批
approved_character = character_controller.approve_character(
    proposal_id=selected_proposal,
    user_modifications=user_changes
)
```

### Epic 3: AI生成核心
**架构组件：**
- **GenerationController** - 生成业务逻辑
- **分层架构** - 交互层→业务层→服务层→数据层
- **向量检索** - 现有ChromaDB增强
- **一致性检查** - 跨章节一致性验证

**关键实现：**
```python
# 章节生成流程
generation_controller = GenerationController(
    llm_service=llm_service,
    vector_service=vector_service,
    character_service=character_service
)

chapter_content = generation_controller.generate_chapter({
    'chapter_number': 5,
    'blueprint': chapter_blueprint,
    'context_strategy': 'character_focused'
})
```

### Epic 4: LLM集成
**架构组件：**
- **LLMService** - LLM服务管理
- **BaseLLMAdapter** - 统一适配器接口
- **LLMManager** - 适配器管理器
- **配置自动保存** - 2秒延迟保存机制

**关键实现：**
```python
# LLM服务使用
llm_service = LLMService()
adapter = llm_service.get_adapter('deepseek', config)

result = adapter.generate(prompt, temperature=0.8, max_tokens=2000)

# 配置自动保存
config_widget.on_config_changed('deepseek', new_config)
# 2秒后自动保存到文件
```

### Epic 5: 用户体验
**架构组件：**
- **ThemeManager** - 主题管理器
- **ThemedWidget** - 主题化基础组件
- **分层UI架构** - 基础层→功能层→界面层
- **Material Design** - 统一设计语言

**关键实现：**
```python
# 主题切换
theme_manager = ThemeManager()
theme_manager.set_theme('dark')

# 所有ThemedWidget自动更新
class CharacterListWidget(ThemedWidget):
    def apply_theme(self, theme_name):
        style = self.theme_manager.get_style('QListWidget::item:selected')
        self.setStyleSheet(style)
```

### Epic 6: 系统稳定性
**架构组件：**
- **错误处理模式** - 统一异常处理
- **日志记录模式** - 结构化日志
- **状态反馈模式** - 状态栏消息
- **性能监控** - 生成时间和资源监控

**关键实现：**
```python
# 统一错误处理
try:
    result = perform_operation()
except SpecificError as e:
    logger.error(f"具体错误: {e}", exc_info=True)
    status_bar.set_error_state("操作失败，请重试")
except Exception as e:
    logger.exception(f"意外错误: {e}")
    status_bar.set_error_state("系统错误，请联系支持")
```

---

## 🔧 技术栈详情

### 核心技术栈
| 技术领域 | 选择 | 版本 | 用途 |
|---------|------|------|------|
| **编程语言** | Python | 3.12+ | 主要开发语言 |
| **UI框架** | PySide6 | 6.8.0 | 桌面应用界面 |
| **AI框架** | LangChain | 0.3.27 | LLM集成框架 |
| **向量数据库** | ChromaDB | 1.0.20 | 语义检索存储 |
| **本地数据库** | SQLite | 3.x | 结构化数据存储 |

### AI服务集成
| 提供商 | 服务类型 | 适配器 | 状态 |
|--------|---------|--------|------|
| **DeepSeek** | LLM + Embedding | DeepSeekAdapter | ✅ 已实现 |
| **OpenAI** | LLM + Embedding | OpenAIAdapter | ✅ 已实现 |
| **Gemini** | LLM + Embedding | GeminiAdapter | ✅ 已实现 |
| **Hugging Face** | LLM + Embedding | HuggingFaceAdapter | ✅ 已实现 |
| **Ollama** | 本地LLM | OllamaAdapter | ✅ 已实现 |

---

## 📊 数据架构设计

### 数据存储策略
```python
# 混合存储架构
project_data/
├── project.db                    # SQLite数据库
│   ├── projects                  # 项目表
│   ├── characters                # 角色表
│   ├── generation_history        # 生成历史表
│   └── user_preferences          # 用户偏好表
├── chapters/                     # 章节文件
│   ├── chapter_1.txt            # 章节内容
│   ├── chapter_1_meta.json      # 章节元数据
│   └── ...
├── vectorstore/                  # ChromaDB向量存储
│   ├── chapters                 # 章节向量
│   └── knowledge                 # 知识库向量
├── exports/                      # 导出文件
└── backups/                      # 备份文件
```

### 核心数据模型
```python
# 角色数据模型
class CharacterModel:
    id: str                    # 唯一标识
    project_id: str            # 所属项目
    name: str                  # 角色名称
    character_type: str         # 角色类型（主角/配角/反派）
    natural_description: str   # 用户自然语言描述
    ai_proposals: List[str]    # AI生成的提案列表
    approved_proposal: str      # 用户批准的提案
    traits: dict               # 性格特征字典
    relationships: dict        # 关系网络字典
    status: str                # 状态（draft/approved/archived）
    created_at: datetime       # 创建时间

# 项目数据模型
class ProjectModel:
    id: str                    # 唯一标识
    name: str                  # 项目名称
    description: str           # 项目描述
    genre: str                 # 小说类型
    total_chapters: int        # 总章节数
    config: dict              # 项目配置
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

---

## 🎨 UI架构设计

### 分层组件架构
```python
# 三层UI架构
# 1. 基础层：可复用组件
class ThemedWidget(QWidget):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.theme_manager.theme_changed.connect(self.apply_theme)

# 2. 功能层：业务组件
class CharacterController:
    def generate_proposals(self, description):
        # AI生成角色提案逻辑
        pass

# 3. 界面层：用户界面组装
class CharacterManagerUI(QWidget):
    def __init__(self, character_controller, theme_manager):
        # 组装基础组件构建完整界面
        self.character_list = SearchableListWidget(theme_manager)
        self.approval_panel = CharacterApprovalWidget(theme_manager)
```

### 主题管理系统
```python
class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": LightTheme(),
            "dark": DarkTheme()
        }
        self.theme_changed = pyqtSignal(str)

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme_changed.emit(theme_name)
        self.save_theme_preference(theme_name)

    def get_style(self, widget_type, state="normal"):
        return self.themes[self.current_theme].get_style(widget_type, state)
```

---

## 🔄 实现模式（AI代理一致性规则）

### 命名模式
```python
# 统一命名约定
class NamingPatterns:
    # 文件命名
    CHARACTER_FILES = "character_{character_id}.json"
    CHAPTER_FILES = "chapter_{chapter_num}.txt"

    # 数据库表名
    TABLES = {
        'projects': 'projects',
        'characters': 'characters',
        'generation_history': 'generation_history'
    }

    # API端点（如果需要）
    ENDPOINTS = {
        'characters': '/api/projects/{project_id}/characters',
        'chapters': '/api/projects/{project_id}/chapters'
    }
```

### 结构模式
```python
# 统一目录结构
class ProjectStructure:
    BASE_DIRS = ['chapters/', 'exports/', 'vectorstore/', 'backups/']
    CONFIG_FILES = ['project.db', 'config.json', 'theme.json']

    @staticmethod
    def ensure_structure(project_path):
        for dir_name in ProjectStructure.BASE_DIRS:
            os.makedirs(os.path.join(project_path, dir_name), exist_ok=True)
```

### 错误处理模式
```python
# 统一错误处理
class ErrorHandler:
    @staticmethod
    def handle_operation(operation_func, error_message, default_return=None):
        try:
            return operation_func()
        except SpecificError as e:
            logging.error(f"{error_message}: {e}", exc_info=True)
            return default_return
        except Exception as e:
            logging.exception(f"意外错误: {e}")
            return default_return
```

### 日志记录模式
```python
# 统一日志格式
class Logger:
    @staticmethod
    def info_operation(operation, details=""):
        logging.info(f"[{operation}] {details}")

    @staticmethod
    def error_operation(operation, error, details=""):
        logging.error(f"[{operation}] {error}: {details}", exc_info=True)

    @staticmethod
    def debug_operation(operation, data):
        logging.debug(f"[{operation}] {data}")
```

### 状态反馈模式
```python
# 统一状态反馈
class StatusFeedback:
    @staticmethod
    def show_operation_start(status_bar, message):
        status_bar.set_info_state(message)

    @staticmethod
    def show_operation_success(status_bar, message):
        status_bar.set_success_state(message)
        QTimer.singleShot(3000, lambda: status_bar.clear_status())

    @staticmethod
    def show_operation_error(status_bar, message):
        status_bar.set_error_state(message)
```

---

## 📈 性能考虑

### 向量检索优化
- **分块策略** - 最大500字符，避免token超限
- **缓存机制** - 常用查询结果缓存
- **异步处理** - 向量计算异步执行
- **批量处理** - 多文档批量向量化

### UI响应性优化
- **延迟加载** - 大数据列表分页加载
- **主题缓存** - 样式表预编译和缓存
- **事件节流** - 搜索输入防抖处理
- **内存管理** - 及时释放不用的UI组件

### 数据库优化
- **索引策略** - 关键查询字段建立索引
- **连接池** - SQLite连接复用
- **批量操作** - 批量插入和更新
- **定期清理** - 过期数据清理机制

---

## 🔒 安全架构

### 数据安全
- **本地存储** - 敏感数据本地化存储
- **配置加密** - API密钥加密存储
- **访问控制** - 项目级别权限控制
- **备份加密** - 备份文件加密保护

### API安全
- **密钥管理** - API密钥安全管理
- **请求限制** - API调用频率限制
- **错误处理** - API错误信息脱敏
- **重试机制** - 网络错误重试策略

---

## 🚀 部署架构

### 应用打包
```python
# PyInstaller配置
# main.spec
a = Analysis(['main.py'],
             pathex=['/path/to/InfiniteQuill'],
             binaries=[],
             datas=[('ui_qt/styles', 'ui_qt/styles')],
             hiddenimports=['PySide6', 'chromadb', 'langchain'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)
```

### 跨平台支持
- **Windows** - .exe安装包，自动注册文件关联
- **macOS** - .app应用包，支持沙盒模式
- **Linux** - .AppImage便携包，包含所有依赖

---

## 📊 Epic实施顺序建议

### 第一阶段：基础设施（1-2周）
1. **Epic 1** - 项目管理基础设施
2. **数据层实现** - HybridDataManager和数据库设计
3. **配置系统** - 自动保存和主题管理基础

### 第二阶段：核心功能（2-3周）
4. **Epic 2** - 角色管理系统
5. **Epic 4** - LLM集成服务
6. **UI基础组件** - ThemedWidget和基础组件库

### 第三阶段：AI生成（2-3周）
7. **Epic 3** - AI生成核心
8. **向量检索增强** - 基于现有代码优化
9. **一致性检查** - 跨章节一致性验证

### 第四阶段：用户体验（1-2周）
10. **Epic 5** - 用户体验优化
11. **主题系统** - 完整的Material Design主题
12. **响应式布局** - 多屏幕尺寸适配

### 第五阶段：系统完善（1周）
13. **Epic 6** - 系统稳定性
14. **错误处理** - 完善的异常处理机制
15. **性能优化** - 最终性能调优

---

## 🧪 测试策略

### 单元测试
- **数据模型测试** - CharacterModel、ProjectModel验证
- **服务层测试** - CharacterService、LLMService测试
- **适配器测试** - LLM适配器功能验证
- **工具函数测试** - 命名模式、验证工具测试

### 集成测试
- **数据流测试** - 端到端数据操作验证
- **UI集成测试** - 组件交互和数据绑定
- **AI服务集成** - LLM调用和向量检索测试
- **主题切换测试** - 主题系统完整性验证

### 用户验收测试
- **Epic功能验收** - 每个Epic的完整功能验证
- **性能验收** - 响应时间和资源使用验证
- **兼容性验收** - 多平台兼容性测试
- **用户场景验收** - 真实用户使用场景验证

---

## 📋 架构决策记录（ADR）

### ADR-001: 角色管理数据模型选择
**决策：** 采用混合设计（SQLite基础表 + JSON详情文档）
**理由：** 平衡查询性能和数据灵活性，支持复杂角色关系
**后果：** 需要维护两套存储机制，但获得最佳性能

### ADR-002: AI生成流程架构
**决策：** 采用四层分层架构
**理由：** 职责分离清晰，易于测试和维护
**后果：** 增加了代码复杂度，但提高了可维护性

### ADR-003: 多LLM适配器设计
**决策：** 采用适配器模式
**理由：** 统一接口，易于扩展新的LLM提供商
**后果：** 需要维护适配器接口，但获得良好的扩展性

### ADR-004: 向量检索策略
**决策：** 保持现有基础向量检索
**理由：** 现有实现成熟稳定，充分利用已有投资
**后果：** 可能错过一些高级特性，但降低实施风险

### ADR-005: UI组件架构
**决策：** 采用三层分层组件架构
**理由：** 职责分离，主题统一管理，易于测试
**后果：** 增加了抽象层次，但提高了代码复用性

### ADR-006: 数据持久化策略
**决策：** 采用混合存储策略
**理由：** 发挥各种存储方式的优势，保持兼容性
**后果：** 需要维护多种存储机制，但获得最佳性能

---

## 🎯 成功指标

### 技术指标
- **代码覆盖率** ≥ 80%
- **UI响应时间** ≤ 200ms
- **AI生成时间** ≤ 30秒/章节
- **内存使用** ≤ 500MB（正常运行）
- **启动时间** ≤ 5秒

### 质量指标
- **Bug密度** ≤ 1 bug/KLOC
- **用户界面一致性** 100%
- **数据完整性** 100%
- **跨平台兼容性** 95%

### 用户体验指标
- **学习曲线** 新用户15分钟上手
- **操作效率** 相比现有工具提升50%
- **错误恢复** 90%错误可自动恢复
- **满意度** 用户满意度 ≥ 4.5/5

---

## 📚 参考文档

### 内部文档
- [PRD.md](./PRD.md) - 产品需求文档
- [epics.md](./epics.md) - Epic和用户故事分解
- [index.md](./index.md) - 项目文档索引

### 技术文档
- [architecture.md](./architecture.md) - 现有架构文档
- [component-inventory.md](./component-inventory.md) - 组件清单
- [development-guide.md](./development-guide.md) - 开发指南

### 外部资源
- [PySide6官方文档](https://doc.qt.io/qtforpython/)
- [LangChain文档](https://python.langchain.com/)
- [ChromaDB文档](https://docs.trychroma.com/)

---

## 🔄 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2025-11-18 | 初始架构决策文档 | John (PM Agent) |

---

## 📞 支持联系

**架构相关问题：**
- 查看本文档的对应章节
- 参考开发指南和组件清单
- 联系技术支持团队

**文档更新：**
- 架构变更时更新对应ADR
- 每个Epic完成后更新实施状态
- 定期审查和优化架构设计

---

**文档状态：** ✅ 完成 - 已准备进入实施阶段
**下一步行动：** 开始Epic 1的实施开发
**审查周期：** 每个Epic完成后进行架构审查