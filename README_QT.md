# InfiniteQuill - PySide6现代化界面

## 📁 新UI架构

```
ui_qt/
├── __init__.py              # 模块初始化
├── main_window.py           # 主窗口控制器
├── widgets/                # 自定义组件库
│   ├── config_widget.py     # 配置管理组件
│   ├── generation_widget.py # 生成操作组件
│   ├── chapter_editor.py   # 章节编辑器
│   ├── role_manager.py     # 角色管理器
│   └── status_bar.py       # 状态栏组件
├── dialogs/               # 对话框集合
│   ├── settings_dialog.py  # 设置对话框
│   ├── role_import_dialog.py # 角色导入对话框
│   └── progress_dialog.py  # 进度对话框
├── utils/                 # 工具模块
│   ├── theme_manager.py    # 主题管理器
│   └── ui_helpers.py      # UI辅助函数
└── styles/                # 样式表资源
    ├── material_light.qss  # 浅色主题
    └── material_dark.qss   # 深色主题
```

## 🛠️ 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements_qt.txt
```

### 2. 启动新界面

#### 直接运行
```bash
python main_qt.py
```

### 3. 配置文件

新界面完全兼容现有的`config.json`配置文件，无需重新配置。

## 🎯 核心功能模块

### 🚀 生成操作 (GenerationWidget)
- **架构生成**: 创建小说世界观、角色设定
- **章节规划**: 制定章节大纲和发展脉络
- **章节生成**: 智能生成章节内容
- **批量操作**: 知识库导入、一致性检查

### ⚙️ 配置管理 (ConfigWidget)
- **LLM配置**: 支持OpenAI、DeepSeek、Gemini等
- **嵌入配置**: 向量模型和检索参数设置
- **代理设置**: HTTP/SOCKS代理配置
- **高级设置**: 日志、性能、界面参数

### 📝 章节编辑器 (ChapterEditor)
- **多格式编辑**: 富文本编辑器
- **实时预览**: Markdown渲染预览
- **版本管理**: 编辑历史和版本对比
- **导出功能**: Word、PDF、Markdown格式

### 👥 角色管理 (RoleManager)
- **角色库**: 分类管理所有角色
- **关系网络**: 可视化角色关系
- **导入导出**: 支持多种文件格式
- **AI生成**: 智能角色创建

## 🎨 主题系统

### 浅色主题
- 清爽简洁的视觉体验
- 适合白天使用
- 降低视觉疲劳

### 深色主题
- 护眼夜间模式
- 现代科技感
- 减少屏幕眩光

### 自定义主题
- 支持自定义颜色
- 字体大小调节
- 布局间距配置

## ⚡ 性能优化

### 1. 异步处理
- LLM调用不阻塞界面
- 后台任务进度显示
- 可取消的长时间操作

### 2. 内存管理
- 智能缓存策略
- 大文件分页加载
- 自动内存回收

### 3. 渲染优化
- 虚拟化列表显示
- 延迟加载组件
- GPU硬件加速

## 🔧 快捷键

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 新建项目 | Ctrl+N | 创建新的小说项目 |
| 打开项目 | Ctrl+O | 打开现有项目 |
| 保存 | Ctrl+S | 保存当前文件/设置 |
| 撤销 | Ctrl+Z | 撤销上一步操作 |
| 重做 | Ctrl+Y | 重做上一步操作 |
| 复制 | Ctrl+C | 复制选中内容 |
| 粘贴 | Ctrl+V | 粘剪板内容粘贴 |
| 查找 | Ctrl+F | 在文档中查找 |
| 替换 | Ctrl+H | 查找并替换 |
| 全选 | Ctrl+A | 选择全部内容 |
| 加粗 | Ctrl+B | 文本加粗 |
| 斜体 | Ctrl+I | 文字斜体 |
| 下划线 | Ctrl+U | 添加下划线 |

## 🐛 故障排除

### 常见问题

#### 1. 中文显示异常
```bash
# 确保系统安装了中文字体
# Windows: 系统自带微软雅黑
# macOS: 系统自带苹方字体
# Linux: 安装noto-sans-cjk
```

#### 2. 界面启动失败
```bash
# 检查PySide6版本
python -c "import PySide6; print(PySide6.__version__)"

# 重新安装依赖
pip uninstall PySide6 PySide6-Addons
pip install PySide6==6.8.0 PySide6-Addons==6.8.0
```

#### 3. 性能问题
```bash
# 启用硬件加速
export QT_OPENGL=angle  # Windows
export QT_OPENGL=desktop  # Linux/macOS
```

### 调试模式

```bash
# 启用调试日志
python main_qt.py --debug

# 显示性能指标
python main_qt.py --profile
```

## 📱 平台兼容性

### Windows
- ✅ Windows 10/11
- ✅ 支持High DPI
- ✅ 原生文件对话框

### macOS
- ✅ macOS 10.15+
- ✅ Retina显示支持
- ✅ 原生菜单栏

### Linux
- ✅ Ubuntu 20.04+
- ✅ 支持Wayland/X11
- ✅ 系统主题集成

## 🔮 未来计划

### v2.1 版本
- [ ] 插件系统支持
- [ ] 云端同步功能
- [ ] 协作编辑模式
- [ ] 多语言界面

### v2.2 版本
- [ ] AI语音合成
- [ ] 插图生成集成
- [ ] 移动端适配
- [ ] Web版本发布

## 🤝 贡献指南

欢迎参与PySide6界面改进！

1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 发起Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd InfiniteQuill

# 安装开发依赖
pip install -r requirements_qt.txt

# 代码格式化
black ui_qt/
isort ui_qt/
```

## 📄 许可证

本项目遵循原项目的许可证条款。

---
