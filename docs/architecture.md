# InfiniteQuill - 架构文档

**项目类型**: Python桌面应用（AI驱动的小说生成器）
**主要技术**: Python 3.12+, PySide6 6.8.0, LangChain, ChromaDB
**架构模式**: 模块化桌面应用，分为UI层和AI生成层

---

## 1. 执行摘要

InfiniteQuill是一个AI驱动的小说创作桌面应用，使用PySide6构建现代化GUI界面。该应用集成了多个LLM提供商（OpenAI, DeepSeek, Gemini等）和向量数据库（ChromaDB），提供从架构生成到章节创作的完整小说创作流程。

**核心功能**: AI架构生成 → 章节蓝图 → 智能章节创作 → 一致性检查

---

## 2. 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **语言** | Python | 3.12+ | 主要开发语言 |
| **UI框架** | PySide6 | 6.8.0 | Qt桌面UI框架 |
| **AI框架** | LangChain | 0.3.27 | LLM应用框架 |
| **向量数据库** | ChromaDB | 1.0.20 | 文本向量存储与检索 |
| **AI模型** | Transformers | 4.56.1 | Hugging Face模型库 |
| **嵌入** | Sentence Transformers | 5.1.0 | 文本嵌入生成 |
| **LLM提供商** | OpenAI, DeepSeek, Gemini | - | 多LLM支持 |
| **配置** | PyYAML, python-dotenv | - | 配置管理 |
| **日志** | coloredlogs, rich | - | 日志记录 |

---

## 3. 架构模式

应用采用**模块化架构**，主要分为两大模块：

1. **UI层 (`ui_qt/`)** - PySide6构建的桌面界面
   - 主窗口与导航
   - 配置管理界面
   - 小说生成控制面板
   - 章节编辑器
   - 角色管理器

2. **AI生成层 (`novel_generator/`)** - 小说生成核心逻辑
   - 架构生成模块
   - 章节蓝图模块
   - 章节内容生成模块
   - 知识管理（向量检索）
   - 一致性检查模块

**数据流向**:
```
用户输入 → UI层 → ProjectManager → ConfigManager → AI生成层
                     ↓                        ↓
              项目文件管理 ← ← ← LLM配置 + 嵌入配置
                     ↓
              状态显示（StatusBar）
```

---

## 4. 数据架构

### 4.1 项目结构

每个小说项目是一个独立文件夹，包含：

```
项目根目录/
├── project.json              # 项目配置文件
├── Novel_architecture.txt    # AI生成的小说架构
├── Novel_directory.txt       # 章节蓝图
├── global_summary.txt        # 全局摘要
├── character_state.txt       # 角色状态
└── chapters/                 # 章节文件
    ├── chapter_001.txt
    ├── chapter_002.txt
    └── ...
```

### 4.2 配置文件结构 (`config.json`)

```json
{
  "last_interface_format": "OpenAI",
  "last_embedding_interface_format": "OpenAI",
  "llm_configs": {
    "DeepSeek V3": {
      "api_key": "",
      "base_url": "https://api.deepseek.com/v1",
      "model_name": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 8192,
      "timeout": 600,
      "interface_format": "OpenAI"
    },
    // ...其他LLM配置
  },
  "embedding_configs": {
    "OpenAI": {
      "api_key": "",
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
  },
  "proxy_setting": {...},
  "webdav_config": {...}
}
```

### 4.3 向量存储（ChromaDB）

- **用途**: 存储生成内容（架构、蓝图、章节）的向量嵌入
- **功能**: 在生成新内容时检索相关信息，确保连贯性
- **集成**: 通过LangChain与ChromaDB集成

---

## 5. 组件概览

### 5.1 UI组件 (`ui_qt/`)

| 组件 | 文件 | 功能 |
|------|------|------|
| **主窗口** | `main_window.py` | 应用主窗口，协调各组件 |
| **配置组件** | `widgets/config_widget.py` | LLM和嵌入配置界面 |
| **生成组件** | `widgets/generation_widget.py` | 小说生成控制面板 |
| **章节编辑器** | `widgets/chapter_editor.py` | 富文本章节编辑器 |
| **角色管理器** | `widgets/role_manager.py` | 角色库管理界面 |
| **状态栏** | `widgets/status_bar.py` | 应用状态显示 |
| **设置对话框** | `dialogs/settings_dialog.py` | 应用设置 |
| **进度对话框** | `dialogs/progress_dialog.py` | 长时间操作进度 |
| **角色导入** | `dialogs/role_import_dialog.py` | 角色批量导入 |
| **主题管理** | `utils/theme_manager.py` | 深色/浅色主题切换 |

### 5.2 AI生成组件 (`novel_generator/`)

| 组件 | 文件 | 功能 |
|------|------|------|
| **架构生成** | `architecture.py` | 生成小说世界观和设定 |
| **蓝图生成** | `blueprint.py` | 创建章节大纲和发展脉络 |
| **章节生成** | `chapter.py` | 智能生成章节内容 |
| **最终化** | `finalization.py` | 章节质量优化和润色 |
| **知识管理** | `knowledge.py` | 向量检索与知识库 |
| **向量工具** | `vectorstore_utils.py` | ChromaDB操作封装 |
| **项目管理** | `project_manager.py` | 项目文件管理 |
| **数据管理** | `data_manager.py` | 数据持久化 |
| **一致性检查** | `consistency_checker.py` | 检测生成内容一致性 |

### 5.3 适配器层

| 组件 | 文件 | 功能 |
|------|------|------|
| **LLM适配器** | `llm_adapters.py` | 统一LLM接口（OpenAI/DeepSeek/Gemini） |
| **嵌入适配器** | `embedding_adapters.py` | 统一嵌入模型接口 |

---

## 6. 部署架构

### 6.1 环境要求

- **Python版本**: 3.12+
- **依赖安装**: `pip install -r requirements.txt`
- **平台支持**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)

### 6.2 启动流程 (`main.py`)

```
1. show_startup_info()    → 显示启动信息
2. setup_logging()        → 配置日志系统
3. check_dependencies()   → 验证依赖模块
4. QApplication()         → 创建Qt应用实例
5. setup_translator()     → 设置国际化
6. load_config()          → 加载用户配置
7. MainWindow()           → 创建主窗口
8. app.exec()             → 启动事件循环
```

### 6.3 配置文件管理

支持跨平台配置目录：

- **Windows**: `%APPDATA%/InfinitQuill/config.json`
- **macOS**: `~/Library/Preferences/InfinitQuill/config.json`
- **Linux**: `~/.config/InfinitQuill/config.json`

**配置加载逻辑**: 如果用户配置不存在，则从项目目录复制默认配置。

---

## 7. 开发工作流

### 7.1 项目结构

```
InfiniteQuill/
├── ui_qt/                    # UI层 (10,635行)
│   ├── main_window.py
│   ├── widgets/             # UI组件
│   ├── dialogs/             # 对话框
│   ├── utils/               # UI工具
│   └── styles/              # 主题样式
├── novel_generator/         # AI生成层 (2,720行)
│   ├── architecture.py
│   ├── blueprint.py
│   ├── chapter.py
│   ├── knowledge.py
│   └── vectorstore_utils.py
├── main.py                  # 应用入口
├── config_manager.py        # 配置管理
├── project_manager.py       # 项目管理
├── llm_adapters.py          # LLM适配器
├── embedding_adapters.py    # 嵌入适配器
├── prompt_definitions.py    # 提示词定义
├── requirements.txt         # Python依赖
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

### 7.2 核心模块交互

```
┌─────────────────────────────────────────────────────────────┐
│  main.py (应用程序入口)                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─→ config_manager.load_config()
                     │
                     ├─→ ui_qt.MainWindow()
                     │
                     └─→ app.exec()

┌─────────────────────────────────────────────────────────────┐
│  MainWindow (Qt主窗口)                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─→ ConfigWidget (LLM配置)
                     │
                     ├─→ GenerationWidget (生成控制)
                     │
                     ├─→ ChapterEditor (章节编辑)
                     │
                     └─→ RoleManager (角色管理)

┌─────────────────────────────────────────────────────────────┐
│  GenerationWidget                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─→ novel_generator.architecture.generate()
                     │
                     ├─→ novel_generator.blueprint.generate()
                     │
                     ├─→ novel_generator.chapter.generate()
                     │
                     └─→ novel_generator.finalization.process()

┌─────────────────────────────────────────────────────────────┐
│  novel_generator (AI生成层)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─→ llm_adapters (LLM统一接口)
                     │
                     ├─→ embedding_adapters (嵌入统一接口)
                     │
                     └─→ ChromaDB (向量存储)
```

### 7.3 关键设计决策

1. **配置管理**: 使用跨平台配置目录，支持自动创建默认配置
2. **LLM抽象**: 通过适配器模式统一不同LLM提供商的接口
3. **向量检索**: 使用ChromaDB存储生成内容，确保跨章节连贯性
4. **异步生成**: 长时间操作（如LLM调用）使用线程避免UI阻塞
5. **主题系统**: 支持Material Design浅色/深色主题切换

---

## 8. 测试策略

### 8.1 手动测试清单

- [ ] 跨平台配置文件创建和加载
- [ ] LLM配置测试功能（验证API密钥和端点）
- [ ] 嵌入配置测试功能
- [ ] 小说架构生成流程
- [ ] 章节蓝图生成流程
- [ ] 章节内容生成（单章节和多章节）
- [ ] 向量检索连贯性验证
- [ ] UI主题切换（浅色/深色）
- [ ] 项目创建、保存、加载
- [ ] 角色管理（创建、编辑、导入）
- [ ] 章节编辑器功能（富文本编辑、预览）
- [ ] 长时间操作取消功能
- [ ] 错误处理和用户反馈

---

## 9. 已知问题和技术债务

### 9.1 待优化项

1. **性能**: 大项目文件加载时可考虑分页或延迟加载
2. **错误恢复**: 生成过程中断后恢复机制
3. **缓存**: 频繁访问的向量检索结果可添加缓存层
4. **测试覆盖**: 自动化测试覆盖率较低

---

## 10. 未来改进方向

### 10.1 计划功能 (README.md)

**v2.1版本**:
- [ ] 插件系统支持
- [ ] 云端同步功能
- [ ] 协作编辑模式
- [ ] 多语言界面

**v2.2版本**:
- [ ] AI语音合成
- [ ] 插图生成集成
- [ ] 移动端适配
- [ ] Web版本发布

---

**文档生成时间**: 2025-11-16
**扫描级别**: Deep (读取关键文件)
**代码行数**: ~13,355行 (UI: 10,635, Generator: 2,720)
