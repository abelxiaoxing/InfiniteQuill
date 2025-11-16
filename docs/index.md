# InfiniteQuill - 项目文档索引

**项目**: InfiniteQuill - AI驱动的小说生成器
**类型**: Python桌面应用（PySide6）
**架构**: 模块化设计（UI层 + AI生成层）

---

## 📌 快速参考

### 项目概览

- **主要语言**: Python 3.12+
- **UI框架**: PySide6 6.8.0 (Qt)
- **AI框架**: LangChain 0.3.27
- **向量数据库**: ChromaDB 1.0.20
- **代码规模**: ~13,355行（UI: 10,635行，AI: 2,720行）
- **架构模式**: 模块化桌面应用

### 核心功能

1. **多LLM支持**: DeepSeek, OpenAI, Gemini, Hugging Face
2. **小说架构生成**: AI生成世界观和设定
3. **章节蓝图**: 自动生成章节目录和大纲
4. **智能章节创作**: 向量检索确保跨章节连贯性
5. **角色管理**: 角色库、关系网络、AI生成
6. ** Material Design UI**: 浅色/深色主题

---

## 📚 生成的文档

### 架构文档

- [**架构总览**](./architecture.md)
  - 执行摘要和技术栈
  - 架构模式（模块化设计）
  - 数据架构（项目结构、配置文件、向量存储）
  - 组件概览（UI组件、AI生成组件）
  - 部署架构和开发工作流

### 组件清单

- [**组件详细清单**](./component-inventory.md)
  - UI层组件（主窗口、Widgets、Dialogs）
  - AI生成层组件（架构、蓝图、章节生成）
  - 适配器层（LLM适配器、嵌入适配器）
  - 代码规模统计（按模块统计）
  - 外部依赖清单

### 开发指南

- [**开发指南**](./development-guide.md)
  - 环境搭建和依赖安装
  - 项目结构导航
  - 配置管理（跨平台配置）
  - 添加新功能（UI组件、AI模块）
  - LLM适配器扩展（添加新提供商）
  - 调试和测试技巧
  - 性能优化
  - 贡献指南

---

## 🎨 现有文档

- [**README.md**](../README.md)
  - 新UI架构说明
  - 安装和使用指南
  - 核心功能模块介绍
  - 快捷键列表
  - 故障排除
  - 平台兼容性

---

## 🚀 核心模块

### 入口点

| 模块 | 文件 | 功能 |
|------|------|------|
| **应用程序入口** | `main.py` | 应用启动、初始化、主事件循环 |
| **配置管理** | `config_manager.py` | 跨平台配置加载和保存 |
| **项目管理** | `project_manager.py` | 小说项目生命周期管理 |
| **主窗口UI** | `ui_qt/main_window.py` | 主窗口UI，协调各组件 |

### UI层 (`ui_qt/`)

| 模块 | 文件 | 功能 |
|------|------|------|
| **配置组件** | `widgets/config_widget.py` | LLM和嵌入配置界面 |
| **生成组件** | `widgets/generation_widget.py` | 小说生成控制面板 |
| **章节编辑器** | `widgets/chapter_editor.py` | 富文本章节编辑器 |
| **角色管理器** | `widgets/role_manager.py` | 角色库管理界面 |
| **状态栏** | `widgets/status_bar.py` | 应用状态显示 |

### AI生成层 (`novel_generator/`)

| 模块 | 文件 | 功能 |
|------|------|------|
| **架构生成** | `architecture.py` | AI生成世界观和设定 |
| **蓝图生成** | `blueprint.py` | 章节大纲生成 |
| **章节生成** | `chapter.py` | 智能生成章节内容 |
| **知识管理** | `knowledge.py` | 向量检索与知识库 |
| **一致性检查** | `consistency_checker.py` | 检测生成内容一致性 |

---

## 📦 模块架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (应用入口)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ├─────→ config_manager.load_config()
                           │
                           ├─────→ ui_qt.MainWindow()
                           │
                           └─────→ app.exec()

┌─────────────────────────────────────────────────────────────┐
│               ui_qt.MainWindow (主窗口)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ├─────→ ConfigWidget (LLM配置)
                           │
                           ├─────→ GenerationWidget (生成控制)
                           │
                           ├─────→ ChapterEditor (章节编辑)
                           │
                           └─────→ RoleManager (角色管理)

┌─────────────────────────────────────────────────────────────┐
│          novel_generator (AI生成核心)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ├─────→ architecture.generate()
                           │
                           ├─────→ blueprint.generate()
                           │
                           ├─────→ chapter.generate()
                           │
                           └─────→ consistency_checker.check()
```

---

## 🎓 入门路径

### 路径1: 了解AI生成流程

1. 阅读 [架构文档](./architecture.md) 的"数据架构"和"组件概览"部分
2. 查看 `novel_generator/chapter.py` 了解章节生成逻辑
3. 阅读 `prompt_definitions.py` 了解提示词模板
4. 运行应用并观察生成流程

### 路径2: UI定制与扩展

1. 阅读 [组件清单](./component-inventory.md) 的UI层部分
2. 查看 `ui_qt/main_window.py` 了解主窗口组织
3. 阅读 `ui_qt/widgets/generation_widget.py` 了解Widget开发
4. 参考 [开发指南](./development-guide.md) 的"添加新UI组件"部分

### 路径3: 集成新LLM提供商

1. 阅读 [架构文档](./architecture.md) 的"适配器层"部分
2. 查看 `llm_adapters.py` 了解适配器模式
3. 阅读 [开发指南](./development-guide.md) 的"LLM适配器扩展"部分
4. 在 `config_widget.py` 添加配置UI

---

## 🔧 配置与部署

### 配置文件

配置存储在跨平台目录：

```
Windows: %APPDATA%/InfinitQuill/config.json
macOS: ~/Library/Preferences/InfinitQuill/config.json
Linux: ~/.config/InfinitQuill/config.json
```

### 首次运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

### 调试模式

```bash
# 启用详细日志
python main.py --debug

# 显示性能指标
python main.py --profile
```

---

## 🐛 故障排除

### 常见问题

1. **缺少依赖模块**
   ```bash
   # 错误: ImportError: No module named 'PySide6'
   # 解决: pip install PySide6==6.8.0
   ```

2. **API调用失败**
   ```bash
   # 错误: APIError: 401 Unauthorized
   # 解决: 检查config.json中的API密钥
   ```

3. **配置文件权限错误**
   - Windows: 以管理员身份运行
   - macOS/Linux: 检查配置目录权限

完整故障排除: [README.md](../README.md) 的"故障排除"部分

---

## 📈 项目统计

| 指标 | 值 |
|------|------|
| **总代码行数** | ~13,355行 |
| **UI层** | 10,635行 (79.6%) |
| **AI生成层** | 2,720行 (20.4%) |
| **Python模块数** | ~42个 |
| **UI组件数** | ~15个主要组件 |
| **AI生成模块** | ~8个核心模块 |

---

## 🎯 下一步行动

根据你的工作目标：

### 开始新项目规划

- 查看 [架构文档](./architecture.md) 了解现有架构
- 使用 BMad Method 创建PRD文档
- 在现有基础上规划新功能

### 修复Bug或增强功能

- 浏览 [组件清单](./component-inventory.md) 定位相关组件
- 阅读 [开发指南](./development-guide.md) 了解开发流程
- 在 `config_manager.py` 和 `project_manager.py` 查看核心逻辑

### 集成新LLM提供商

- 阅读 [开发指南](./development-guide.md) 的"LLM适配器扩展"部分
- 查看 `llm_adapters.py` 了解适配器模式
- 在 `config_widget.py` 添加配置UI

---

## 📞 帮助与支持

- **GitHub Issues**: 报告bug或请求功能
- **现有文档**: README.md包含安装、使用、故障排除
- **开发指南**: [development-guide.md](./development-guide.md)包含详细开发说明

---

**文档生成时间**: 2025-11-16
**扫描级别**: Deep (读取关键文件)
**项目文档版本**: 1.0
