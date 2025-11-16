# InfiniteQuill - 组件清单

**总代码行数**: ~13,355行
- UI层: 10,635行
- AI生成层: 2,720行

---

## 1. UI层组件 (`ui_qt/`)

### 1.1 主窗口 (`main_window.py`)

**功能**: 应用程序主窗口，协调各UI组件

**关键类/函数**:
- `MainWindow` - 主窗口类
  - 初始化UI组件
  - 管理菜单栏、工具栏
  - 协调各widget之间的通信
  - 处理窗口事件（关闭、调整大小等）

**依赖**:
- PySide6.QtWidgets: QMainWindow, QApplication
- ui_qt.widgets.*: 各种widget组件
- config_manager: 配置加载

---

### 1.2 Widget组件 (`ui_qt/widgets/`)

#### 1.2.1 Configuration Widget (`config_widget.py`)

**功能**: LLM和嵌入配置管理界面

**关键特性**:
- LLM提供商配置（OpenAI/DeepSeek/Gemini）
  - API密钥输入
  - Base URL配置
  - 模型名称选择
  - 温度、max_tokens、超时设置
- 嵌入模型配置
  - API密钥和模型名称
  - 检索参数（retrieval_k）
- 配置测试功能（异步）
- 配置保存与加载

**依赖**:
- config_manager: 配置持久化
- llm_adapters: LLM测试
- embedding_adapters: 嵌入测试

---

#### 1.2.2 Generation Widget (`generation_widget.py`)

**功能**: 小说生成控制面板

**关键特性**:
- 小说架构生成
- 章节大纲生成
- 单个/批量章节生成
- 一致性检查
- 知识库导入
- 生成进度显示
- 生成历史记录

**依赖**:
- novel_generator.*: AI生成模块
- project_manager: 项目管理

---

#### 1.2.3 Chapter Editor (`chapter_editor.py`)

**功能**: 富文本章节编辑器

**关键特性**:
- 多标签页编辑
- 富文本格式支持
- 实时Markdown渲染预览
- 版本历史和对比
- 导出功能（Word/PDF/Markdown）
- 查找/替换功能
- 章节预览

**依赖**:
- PySide6.QtWidgets: QTextEdit, QTabWidget
- project_manager: 章节文件读写

---

#### 1.2.4 Role Manager (`role_manager.py`)

**功能**: 角色库管理界面

**关键特性**:
- 角色列表显示
- 角色详细信息编辑
- 角色分类管理
- 角色关系网络可视化
- 角色导入/导出（多种格式）
- AI智能角色创建
- 角色搜索和过滤

**依赖**:
- project_manager: 角色数据管理
- novel_generator: AI角色生成

---

#### 1.2.5 Status Bar (`status_bar.py`)

**功能**: 应用状态显示和提示

**关键特性**:
- 当前项目信息显示
- LLM配置状态指示
- 生成进度显示
- 错误/警告/成功消息显示
- 操作提示和反馈
- 动画效果（进度指示器）

**依赖**:
- PySide6.QtWidgets: QStatusBar

---

### 1.3 Dialog组件 (`ui_qt/dialogs/`)

#### 1.3.1 Settings Dialog (`settings_dialog.py`)

**功能**: 应用设置对话框

**关键特性**:
- 通用设置（界面、性能等）
- 代理设置（HTTP/SOCKS）
- WebDAV同步配置
- 编辑器设置（字体、主题）
- 快捷键配置

**依赖**:
- config_manager: 配置保存

---

#### 1.3.2 Progress Dialog (`progress_dialog.py`)

**功能**: 长时间操作进度对话框

**关键特性**:
- 进度条显示
- 当前操作步骤文本
- 已用时间/估计剩余时间
- 取消操作按钮
- 详细信息展开区域

**依赖**:
- PySide6.QtWidgets: QProgressDialog

---

#### 1.3.3 Role Import Dialog (`role_import_dialog.py`)

**功能**: 角色批量导入对话框

**关键特性**:
- 选择导入文件（JSON/CSV/Excel）
- 预览导入数据
- 字段映射配置
- 冲突处理策略（覆盖/跳过/合并）
- 导入进度显示

**依赖**:
- project_manager: 角色数据导入

---

### 1.4 Utility组件 (`ui_qt/utils/`)

#### 1.4.1 Theme Manager (`theme_manager.py`)

**功能**: 主题管理系统

**关键特性**:
- 浅色/深色主题切换
- Material Design样式
- 自定义颜色支持
- 主题配置保存
- 运行时主题热切换

**依赖**:
- PySide6.QtCore: QFile

---

#### 1.4.2 UI Helpers (`ui_helpers.py`)

**功能**: UI辅助函数

**关键特性**:
- 对话框创建快捷函数
- UI组件样式应用
- 布局辅助函数
- 国际化支持
- 错误提示显示

**依赖**:
- PySide6.QtWidgets: QMessageBox, QFileDialog

---

## 2. AI生成层组件 (`novel_generator/`)

### 2.1 Architecture Generation (`architecture.py`)

**功能**: 生成小说世界观和设定

**关键特性**:
- 分析用户输入的主题/体裁
- 调用架构LLM生成世界观设定
- 生成角色设定
- 生成故事背景
- 生成主要冲突
- 保存架构文件

**依赖**:
- llm_adapters: LLM调用
- vectorstore_utils: 向量存储

---

### 2.2 Blueprint Generation (`blueprint.py`)

**功能**: 创建章节大纲和发展脉络

**关键特性**:
- 读取小说架构
- 调用蓝图LLM生成章节目录
- 为每个章节生成概要
- 规划章节间的发展逻辑
- 确保章节顺序合理
- 保存蓝图文件

**依赖**:
- llm_adapters: LLM调用
- vectorstore_utils: 相关章节检索

---

### 2.3 Chapter Generation (`chapter.py`)

**功能**: 智能生成章节内容

**关键特性**:
- 读取章节蓝图
- 为单章节生成详细内容
- 批量章节生成
- 使用向量检索确保与之前章节连贯
- 支持用户指导和要求
- 生成进度跟踪

**依赖**:
- llm_adapters: LLM调用
- vectorstore_utils: 上下文检索

---

### 2.4 Finalization (`finalization.py`)

**功能**: 章节质量优化和润色

**关键特性**:
- 章节内容审查
- 语言风格统一
- 逻辑一致性检查
- 错别字和语法修正
- 章节标题优化
- 章节摘要生成

**依赖**:
- llm_adapters: LLM调用

---

### 2.5 Knowledge Management (`knowledge.py`)

**功能**: 向量检索与知识库管理

**关键特性**:
- 文档向量化
- 相似内容检索
- 知识库索引管理
- 多文档联合检索
- 检索结果评分

**依赖**:
- embedding_adapters: 嵌入生成
- vectorstore_utils: ChromaDB操作

---

### 2.6 Vector Store Utilities (`vectorstore_utils.py`)

**功能**: ChromaDB操作封装

**关键特性**:
- ChromaDB集合管理
- 文档添加和删除
- 相似度搜索
- 批量操作优化
- 索引重建

**依赖**:
- chromadb: 向量数据库

---

### 2.7 Project Management (`project_manager.py`)

**功能**: 项目文件管理

**关键特性**:
- 创建新项目
- 保存项目配置
- 加载项目数据
- 更新生成状态
- 计算总字数
- 项目验证

**依赖**:
- utils: 文件操作

---

### 2.8 Data Management (`data_manager.py`)

**功能**: 数据持久化

**关键特性**:
- 文件读写（JSON/TXT）
- 编码处理（UTF-8）
- 数据验证
- 备份管理
- 数据迁移

---

### 2.9 Consistency Checker (`consistency_checker.py`)

**功能**: 检测生成内容一致性

**关键特性**:
- 角色一致性检查
- 情节连贯性验证
- 时间线冲突检测
- 世界观矛盾发现
- 提供修正建议

**依赖**:
- vectorstore_utils: 上下文检索

---

## 3. 适配器层 (Adapters)

### 3.1 LLM Adapters (`llm_adapters.py`)

**功能**: 统一LLM接口

**支持的提供商**:
- OpenAI API格式
- DeepSeek API
- Google Gemini API
- Azure AI Inference
- Hugging Face

**设计模式**: 适配器模式

---

### 3.2 Embedding Adapters (`embedding_adapters.py`)

**功能**: 统一嵌入模型接口

**支持的模型**:
- OpenAI text-embedding-ada-002
- Hugging Face sentence-transformers
- Custom embedding models

**设计模式**: 适配器模式

---

## 4. 配置文件和定义

### 4.1 Prompt Definitions (`prompt_definitions.py`)

**功能**: 所有AI提示词模板

**包含的提示词**:
- 架构生成提示词
- 蓝图生成提示词
- 章节生成提示词
- 一致性检查提示词
- 角色生成提示词

---

### 4.2 Utility Functions (`utils.py`)

**功能**: 通用工具函数

**包含的功能**:
- JSON文件读写
- 文本文件读写
- 数据验证
- 错误处理

---

## 5. 代码规模统计

| 模块 | 文件数 | 代码行数 | 占比 |
|------|--------|----------|------|
| **UI层** | ~30 | 10,635 | 79.6% |
| **AI生成层** | ~12 | 2,720 | 20.4% |
| **总计** | ~42 | 13,355 | 100% |

**说明**: UI层占代码量的约80%，符合桌面应用的特点，AI生成核心逻辑相对集中。

---

## 6. 外部依赖

### 6.1 核心依赖

```
PySide6==6.8.0              # Qt UI框架
langchain==0.3.27          # AI框架
chromadb==1.0.20          # 向量数据库
openai==1.106.1           # OpenAI API
transformers==4.56.1      # Hugging Face模型
sentence-transformers==5.1.0  # 文本嵌入
torch==2.8.0              # PyTorch
```

### 6.2 开发依赖

```
black                     # 代码格式化
isort                     # 导入排序
```

---

## 7. 配置管理

### 7.1 用户配置目录

跨平台配置存储：

- **Windows**: `%APPDATA%/InfinitQuill/config.json`
- **macOS**: `~/Library/Preferences/InfinitQuill/config.json`
- **Linux**: `~/.config/InfinitQuill/config.json`

### 7.2 项目文件结构

每个小说项目独立存储：

```
项目/
├── project.json                        # 项目配置
├── Novel_architecture.txt             # AI生成的架构
├── Novel_directory.txt                # 章节蓝图
├── global_summary.txt                 # 全局摘要
├── character_state.txt               # 角色状态
└── chapters/
    ├── chapter_001.txt
    └── chapter_002.txt
```

---

## 8. 运行流程

### 8.1 启动流程

```
main.py
├── setup_logging()              # 日志初始化
├── check_dependencies()         # 依赖检查
├── QApplication()               # Qt应用创建
├── setup_translator()           # 国际化
├── load_config()                # 配置加载
├── MainWindow()                 # 主窗口创建
└── app.exec()                   # 事件循环
```

### 8.2 小说生成流程

```
GenerationWidget
├── 架构生成 → novel_generator.architecture
├── 蓝图生成 → novel_generator.blueprint
├── 章节批量生成 → novel_generator.chapter
│   └── 向量检索 → ChromaDB (确保连贯性)
├── 最终化 → novel_generator.finalization
└── 一致性检查 → consistency_checker
```

---

**文档生成时间**: 2025-11-16
**扫描级别**: Deep
**总组件数**: ~42个Python模块
