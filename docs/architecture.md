# InfiniteQuill - 决策架构文档

**项目**: InfiniteQuill - AI驱动的智能小说创作平台
**架构类型**: Python桌面应用（PySide6 + AI集成）
**文档类型**: 决策架构文档（AI代理一致性合同）
**生成日期**: 2025-11-18
**架构师**: Winston (BMad Architect Agent)
**目标用户**: AI开发代理

---

## 执行摘要

InfiniteQuill采用**混合式AI架构**，结合统一适配器管理和模块化服务设计，为专业作者提供高效的AI协作创作平台。架构基于成熟的PySide6 GUI框架，集成了ChromaDB向量存储和LangChain AI框架，支持多LLM提供商的灵活切换。

**核心价值**: 通过人机协作模式，将创作效率提升3-5倍，同时保持95%以上的内容质量满意度。

**架构原则**: 稳定优先、用户隐私、易于扩展、专业体验

---

## 项目初始化

### 推荐启动模板
使用pyside-desktop-app作为基础架构：

```bash
# 克隆模板
git clone https://github.com/benuha/pyside-desktop-app.git InfiniteQuill
cd InfiniteQuill

# 安装依赖
pip install -r requirements.txt

# 添加AI相关依赖
pip install langchain langchain-openai langchain-chroma chromadb sentence-transformers

# 启动应用
python -m app.main
```

**模板提供的架构决策**:
- PySide6 GUI框架 ✅
- 浅色/深色主题支持 ✅
- 项目结构组织 ✅
- PyInstaller打包支持 ✅

---

## 决策总结

| 类别 | 决策 | 版本 | 影响史诗 | 理由 |
|------|------|------|----------|------|
| **AI集成架构** | 混合式架构（统一适配器+模块化服务） | v1.0 | Epic 2,3,4 | 兼顾集中管理和模块化优势，易于扩展 |
| **向量数据库** | ChromaDB + 适配器模式 | 1.0.20 | Epic 2,3 | 技术选型正确，功能丰富，性能优秀 |
| **多LLM适配器** | 统一BaseLLMAdapter + 工厂模式 | v1.0 | Epic 3,4 | 支持10+提供商，设计一致，扩展性强 |
| **数据存储格式** | JSON配置 + 文本内容混合存储 | v1.0 | Epic 1,6 | 用户友好，版本控制友好，跨平台兼容 |
| **UI组件架构** | 模块化标签页 + 组件化Widget | v1.0 | Epic 5 | 符合桌面应用最佳实践，用户体验直观 |
| **配置管理系统** | 跨平台配置 + JSON存储 | v1.0 | Epic 1,4 | 企业级兼容性，功能完整，数据安全 |

---

## 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **语言** | Python | 3.12+ | 主要开发语言 |
| **UI框架** | PySide6 | 6.8.0 | Qt桌面UI框架 |
| **AI框架** | LangChain | 0.3.27 | LLM应用框架 |
| **向量数据库** | ChromaDB | 1.0.20 | 文本向量存储与检索 |
| **嵌入** | Sentence Transformers | 5.1.0 | 文本嵌入生成 |
| **LLM提供商** | OpenAI, DeepSeek, Gemini, Azure等 | - | 多LLM支持 |
| **配置** | PyYAML, python-dotenv | - | 配置管理 |
| **日志** | coloredlogs, rich | - | 日志记录 |

---

## 项目结构

```
InfiniteQuill/
├── main.py                     # 应用程序入口
├── config_manager.py           # 跨平台配置管理
├── project_manager.py          # 项目生命周期管理
├── llm_adapters.py             # LLM统一适配器接口
├── embedding_adapters.py       # 嵌入模型适配器
├── prompt_definitions.py       # AI提示词模板
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
├── ui_qt/                      # UI层 (10,635行)
│   ├── main_window.py          # 主窗口控制器
│   ├── widgets/                # UI组件库
│   │   ├── config_widget.py    # 配置管理组件
│   │   ├── generation_widget.py # 生成操作组件
│   │   ├── chapter_editor.py   # 章节编辑组件
│   │   ├── role_manager.py     # 角色管理组件
│   │   └── status_bar.py       # 状态栏组件
│   ├── dialogs/                # 对话框集合
│   │   ├── settings_dialog.py  # 设置对话框
│   │   ├── progress_dialog.py  # 进度对话框
│   │   └── role_import_dialog.py # 角色导入
│   └── utils/                  # UI工具
│       ├── theme_manager.py    # 主题管理
│       └── ui_helpers.py       # UI辅助函数
├── novel_generator/            # AI生成层 (2,720行)
│   ├── architecture.py         # 小说架构生成
│   ├── blueprint.py            # 章节蓝图生成
│   ├── chapter.py              # 章节内容生成
│   ├── finalization.py        # 内容润色优化
│   ├── knowledge.py            # 向量检索与知识库
│   ├── vectorstore_utils.py    # ChromaDB操作封装
│   ├── consistency_checker.py  # 内容一致性检查
│   └── common.py               # 通用工具函数
└── docs/                       # 项目文档
    ├── architecture.md         # 架构文档
    ├── PRD.md                   # 产品需求文档
    ├── epics.md                # 史诗分解文档
    └── index.md                # 文档索引
```

---

## Epic到架构映射

| Epic | 核心组件 | 主要功能 | 技术实现 |
|------|----------|----------|----------|
| **Epic 1: 项目基础设施** | project_manager.py, config_manager.py | 多项目支持、数据持久化 | JSON配置 + 文件系统 |
| **Epic 2: 角色管理** | role_manager.py, novel_generator/* | AI+用户协作、角色库管理 | LLM适配器 + 向量检索 |
| **Epic 3: AI生成核心** | novel_generator/, llm_adapters.py | 架构生成、章节创作 | LangChain + ChromaDB |
| **Epic 4: LLM集成** | llm_adapters.py, embedding_adapters.py | 多LLM支持、配置管理 | 适配器模式 + 工厂模式 |
| **Epic 5: 用户体验** | ui_qt/, theme_manager.py | 界面、编辑、主题 | PySide6 + Material Design |
| **Epic 6: 系统稳定性** | config_manager.py, vectorstore_utils.py | 数据安全、性能优化 | 本地存储 + 错误处理 |

---

## 技术栈详情

### 核心技术栈

**AI集成层**:
- **LangChain**: 提供统一的AI应用开发框架
- **ChromaDB**: 本地向量数据库，确保内容一致性
- **Sentence Transformers**: 高质量文本嵌入

**UI层**:
- **PySide6**: 现代Qt GUI框架，跨平台支持
- **Material Design**: 专业级界面设计语言
- **主题系统**: 支持浅色/深色主题切换

**数据层**:
- **JSON配置**: 人类可读的配置格式
- **文本文件**: 创作内容直接存储，用户友好
- **文件系统**: 本地存储确保隐私安全

### 集成点

**AI服务集成**:
```python
# 统一LLM接口
llm_adapter = create_llm_adapter(
    interface_format="DeepSeek",
    api_key="xxx",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 统一嵌入接口
embedding_adapter = create_embedding_adapter(
    interface_format="OpenAI",
    api_key="xxx",
    model_name="text-embedding-ada-002"
)
```

**UI与业务逻辑集成**:
```python
# 信号槽通信
generation_widget.generation_started.connect(main_window.on_generation_started)
generation_widget.generation_finished.connect(main_window.on_generation_finished)

# 主题统一管理
theme_manager.apply_theme("dark")
theme_manager.update_all_widgets()
```

---

## 实现模式

这些模式确保所有AI代理的一致性实现：

### 适配器模式 (Adapter Pattern)

**LLM适配器**:
```python
class BaseLLMAdapter:
    def invoke(self, prompt: str) -> str:
        raise NotImplementedError

class DeepSeekAdapter(BaseLLMAdapter):
    def invoke(self, prompt: str) -> str:
        return self._client.invoke(prompt)

# 工厂函数
def create_llm_adapter(interface_format: str, ...) -> BaseLLMAdapter:
    if interface_format == "deepseek":
        return DeepSeekAdapter(...)
    elif interface_format == "openai":
        return OpenAIAdapter(...)
```

**嵌入适配器**:
```python
class BaseEmbeddingAdapter:
    def embed_query(self, query: str) -> List[float]:
        raise NotImplementedError

class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    def embed_query(self, query: str) -> List[float]:
        return self._embedding.embed_query(query)
```

### 模块化架构模式

**AI生成模块**:
```python
# 每个生成功能独立模块
novel_generator/
├── architecture.py    # 世界观架构生成
├── blueprint.py       # 章节蓝图生成
├── chapter.py         # 章节内容生成
└── finalization.py    # 内容润色优化
```

**UI组件模块**:
```python
# 每个功能独立组件
ui_qt/widgets/
├── config_widget.py    # 配置管理
├── generation_widget.py # 生成操作
├── chapter_editor.py   # 章节编辑
└── role_manager.py     # 角色管理
```

---

## 一致性规则

### 命名约定

**类命名**:
- 适配器类：`{Provider}Adapter` (如 `DeepSeekAdapter`)
- Widget类：`{Function}Widget` (如 `ConfigWidget`)
- 管理器类：`{Resource}Manager` (如 `ProjectManager`)

**文件命名**:
- 模块文件：小写下划线 (如 `llm_adapters.py`)
- 类文件：驼峰命名 (如 `MainWindow.py`)
- 配置文件：小写下划线 (如 `config.json`)

**方法命名**:
- 公共方法：小写下划线 (如 `create_project()`)
- 私有方法：下划线前缀 (如 `_validate_data()`)
- 信号方法：描述性命名 (如 `generation_started`)

### 代码组织

**目录结构**:
```
{module}/
├── __init__.py
├── {module}.py          # 主模块
├── widgets/             # UI组件 (仅ui_qt)
├── dialogs/             # 对话框 (仅ui_qt)
├── utils/               # 工具函数
└── tests/               # 测试文件
```

**导入顺序**:
1. 标准库导入
2. 第三方库导入
3. 本地模块导入
4. 相对导入

### 错误处理

**统一异常处理模式**:
```python
def operation():
    try:
        # 核心逻辑
        result = perform_operation()
        return result
    except SpecificException as e:
        logger.error(f"操作失败: {e}")
        return None
    except Exception as e:
        logger.error(f"未预期错误: {e}", exc_info=True)
        return None
```

**用户友好的错误信息**:
```python
def show_error_to_user(message: str, details: str = ""):
    """显示用户友好的错误信息"""
    QMessageBox.warning(None, "操作失败", message)
    if details:
        logger.error(f"用户操作失败详情: {details}")
```

### 日志策略

**日志级别**:
- `DEBUG`: 详细的调试信息
- `INFO`: 重要的操作信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

**日志格式**:
```python
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

---

## 数据架构

### 项目数据模型

**项目配置 (project.json)**:
```json
{
    "project_info": {
        "name": "项目名称",
        "title": "小说标题",
        "topic": "主题",
        "genre": "类型",
        "created_at": "2025-11-18T...",
        "last_modified": "2025-11-18T..."
    },
    "settings": {
        "chapter_count": 20,
        "word_count": 3000,
        "worldview": "世界观",
        "writing_style": "写作风格"
    },
    "generation_status": {
        "architecture_generated": true,
        "blueprint_generated": true,
        "generated_chapters": [1, 2, 3],
        "total_words": 15000,
        "last_chapter": 3
    },
    "files": {
        "architecture_file": "Novel_architecture.txt",
        "blueprint_file": "Novel_directory.txt",
        "summary_file": "global_summary.txt",
        "character_state_file": "character_state.txt",
        "chapters_dir": "chapters"
    }
}
```

**应用配置 (config.json)**:
```json
{
    "last_interface_format": "OpenAI",
    "llm_configs": {
        "DeepSeek V3": {
            "api_key": "xxx",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        }
    },
    "embedding_configs": {
        "OpenAI": {
            "api_key": "xxx",
            "model_name": "text-embedding-ada-002",
            "retrieval_k": 4,
            "interface_format": "OpenAI"
        }
    },
    "choose_configs": {
        "prompt_draft_llm": "DeepSeek V3",
        "chapter_outline_llm": "DeepSeek V3",
        "architecture_llm": "Gemini 2.5 Pro",
        "final_chapter_llm": "GPT 5",
        "consistency_review_llm": "DeepSeek V3"
    }
}
```

### 数据关系

**项目-章节关系**:
```
项目 (project.json)
├── 架构文件 (Novel_architecture.txt)
├── 蓝图文件 (Novel_directory.txt)
├── 全局摘要 (global_summary.txt)
├── 角色状态 (character_state.txt)
└── 章节目录 (chapters/)
    ├── chapter_001.txt
    ├── chapter_002.txt
    └── ...
```

**向量数据库结构**:
```
项目目录/vectorstore/
├── chroma.sqlite3          # 向量数据
├── 元数据索引               # 文档元数据
└── 集合 "novel_collection"  # 内容集合
    ├── 架构段落向量
    ├── 章节内容向量
    └── 角色信息向量
```

---

## API契约

### LLM适配器接口

**BaseLLMAdapter**:
```python
class BaseLLMAdapter:
    """LLM适配器基类，所有LLM提供商必须实现此接口"""

    def invoke(self, prompt: str) -> str:
        """
        调用LLM生成响应

        Args:
            prompt: 输入提示词

        Returns:
            str: LLM生成的响应文本

        Raises:
            ConnectionError: 连接失败
            TimeoutError: 请求超时
            APIError: API调用错误
        """
        raise NotImplementedError
```

**嵌入适配器接口**:
```python
class BaseEmbeddingAdapter:
    """嵌入适配器基类，所有嵌入模型必须实现此接口"""

    def embed_query(self, query: str) -> List[float]:
        """生成查询文本的向量嵌入"""
        raise NotImplementedError

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档的向量嵌入"""
        raise NotImplementedError
```

### 项目管理接口

**ProjectManager**:
```python
class ProjectManager:
    """项目管理器，负责项目的生命周期管理"""

    def create_project(self, project_path: str, project_info: Dict) -> bool:
        """创建新项目"""

    def load_project(self, project_path: str) -> Optional[Dict]:
        """加载现有项目"""

    def save_project(self, project_path: str, project_data: Dict) -> bool:
        """保存项目数据"""

    def update_generation_status(self, chapter_num: int, is_completed: bool):
        """更新生成状态"""
```

---

## 安全架构

### 数据安全

**本地存储原则**:
- 所有用户数据仅存储在本地设备
- 配置文件使用用户配置目录，权限控制
- 创作内容以文本格式存储，用户可直接访问

**API密钥保护**:
- API密钥存储在本地配置文件中
- 配置文件权限设置为仅用户可读写
- 不向任何第三方服务传输用户密钥

**数据完整性**:
- 项目配置使用JSON格式，易于验证
- 重要操作前进行数据备份
- 异常情况下的数据恢复机制

### 隐私保护

**无云端依赖**:
- 核心功能完全离线运行
- 仅LLM调用需要网络连接
- 用户创作内容永不离开本地设备

**透明性**:
- 所有配置文件用户可读
- 数据格式开放，易于迁移
- 源代码开源，可独立审计

---

## 性能考虑

### 内存管理

**大型项目优化**:
- 向量数据库分批加载，避免内存溢出
- 章节内容按需加载，不预加载全部内容
- UI组件懒加载，减少启动内存占用

**缓存策略**:
- LLM响应结果缓存，避免重复调用
- 向量检索结果缓存，提高查询速度
- 配置文件缓存，减少磁盘I/O

### 响应性能

**异步处理**:
```python
# 耗时操作使用QThread
class GenerationWorker(QThread):
    progress = Signal(int, str)
    completed = Signal(str)
    error = Signal(str)

    def run(self):
        # 在后台线程执行AI生成
        result = self.generate_content()
        self.completed.emit(result)
```

**UI响应优化**:
- 进度条显示长时间操作状态
- 可取消的操作支持
- 错误处理不影响UI响应

---

## 部署架构

### 打包分发

**PyInstaller配置**:
```python
# 使用启动模板的打包功能
python manage.py --create-exe

# 输出结构
dist/
└── InfiniteQuill/
    ├── InfiniteQuill.exe    # 主程序
    ├── resources/           # 资源文件
    └── _internal/          # 运行时依赖
```

**跨平台支持**:
- Windows: .exe可执行文件
- macOS: .app应用包
- Linux: 可执行文件

### 环境要求

**系统要求**:
- Python 3.12+
- 4GB RAM (推荐8GB+)
- 2GB可用磁盘空间
- 网络连接 (仅LLM调用需要)

**依赖管理**:
```bash
# 核心依赖
pip install PySide6==6.8.0
pip install langchain==0.3.27
pip install chromadb==1.0.20
pip install sentence-transformers==5.1.0

# 可选依赖
pip install nltk  # 文本分段
pip install requests  # API调用
```

---

## 开发环境

### 开发先决条件

**Python环境**:
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**开发工具**:
- **IDE**: VS Code, PyCharm
- **版本控制**: Git
- **UI设计**: Qt Designer
- **调试工具**: Python debugger

### 设置命令

```bash
# 1. 克隆项目
git clone https://github.com/your-org/InfiniteQuill.git
cd InfiniteQuill

# 2. 设置开发环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 运行应用
python main.py

# 4. 开发模式 (启用调试日志)
python main.py --debug

# 5. 运行测试
python -m pytest tests/

# 6. 构建文档
python -m sphinx docs/ build/
```

---

## 架构决策记录 (ADRs)

### ADR-001: AI集成架构选择
**决策**: 采用混合式架构（统一适配器+模块化服务）
**原因**: 兼顾集中管理优势和模块化灵活性，易于扩展新AI模型
**替代方案**: 纯集中式、纯模块化
**影响**: 所有AI相关功能 (Epic 2,3,4)

### ADR-002: 向量数据库选型
**决策**: 使用ChromaDB作为本地向量数据库
**原因**: 开源免费、Python生态好、本地存储保护隐私
**替代方案**: Pinecone、Weaviate、FAISS
**影响**: 内容一致性功能 (Epic 2,3)

### ADR-003: 数据存储格式
**决策**: JSON配置 + 文本内容混合存储
**原因**: 用户友好、版本控制友好、跨平台兼容
**替代方案**: 纯JSON、SQLite数据库、二进制格式
**影响**: 项目管理和数据持久化 (Epic 1,6)

### ADR-004: UI框架选择
**决策**: 使用PySide6构建桌面应用
**原因**: 原生性能、跨平台、专业桌面应用体验
**替代方案**: Web应用、Electron、Tkinter
**影响**: 所有用户界面功能 (Epic 5)

### ADR-005: 配置管理策略
**决策**: 跨平台配置目录 + JSON存储
**原因**: 标准化、用户友好、易于迁移
**替代方案**: 注册表、数据库、云端配置
**影响**: 应用配置和用户设置 (Epic 1,4)

---

---

**文档生成完成时间**: 2025-11-18
**架构师**: Winston (BMad Architect Agent)
**文档版本**: 1.0
**下次更新**: 根据功能增强和用户反馈

---

*本文档是InfiniteQuill项目的架构指导文档，所有AI代理在实现功能时必须严格遵循本文档定义的架构决策和一致性规则。*