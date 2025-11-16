# InfiniteQuill - 开发指南

**目标读者**: Python开发人员、贡献者
**技能要求**: Python 3.12+, PySide6基础, LangChain基础概念

---

## 1. 先决条件

### 1.1 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, 或 Linux (Ubuntu 20.04+)
- **Python版本**: 3.12或更高
- **磁盘空间**: 至少2GB可用空间（用于依赖安装和虚拟环境）
- **网络**: 稳定的互联网连接（用于下载依赖包）

### 1.2 必需技能

- **Python**: 熟练使用Python 3.12+
- **PySide6/Qt**: 了解Qt信号/槽机制、窗口控件基础
- **LangChain**: 理解LLM应用框架的基本概念
- **Git**: 版本控制基础操作

---

## 2. 环境搭建

### 2.1 克隆仓库

```bash
# 克隆项目git clone <repository-url>
cd InfiniteQuill
```

### 2.2 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

### 2.3 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 验证关键依赖安装
python -c "import PySide6; print(f'PySide6: {PySide6.__version__}')"
python -c "import langchain; print(f'LangChain: {langchain.__version__}')"
python -c "import chromadb; print(f'ChromaDB: {chromadb.__version__}')"
```

**安装耗时**: 5-15分钟（取决于网络速度和硬件）

### 2.4 验证安装

```bash
# 运行依赖检查
python main.py --dry-run
```

如果依赖检查通过，你将看到启动信息而无GUI界面（使用`--dry-run`跳过界面启动）。

---

## 3. 项目结构导航

### 3.1 快速定位代码

```
InfiniteQuill/
├── main.py                     # 应用程序入口
├── config_manager.py           # 配置管理（跨平台）
├── project_manager.py          # 项目管理
├── llm_adapters.py             # LLM统一接口
├── embedding_adapters.py       # 嵌入模型接口
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
├── ui_qt/                     # UI层 (10,635行)
│   ├── main_window.py         # 主窗口
│   ├── widgets/               # UI组件
│   ├── dialogs/               # 对话框
│   └── utils/                 # UI工具
├── novel_generator/           # AI生成层 (2,720行)
│   ├── architecture.py        # 架构生成
│   ├── blueprint.py          # 蓝图生成
│   ├── chapter.py            # 章节生成
│   └── consistency_checker.py # 一致性检查
└── README.md                  # 项目说明
```

### 3.2 关键入口点

| 文件 | 用途 | 何时修改 |
|------|------|----------|
| `main.py` | 应用启动逻辑 | 添加启动选项、修改初始化流程 |
| `config_manager.py` | 配置加载和保存 | 添加新配置项、修改配置结构 |
| `ui_qt/main_window.py` | 主窗口UI | 添加新菜单、修改主布局 |
| `novel_generator/chapter.py` | 章节生成核心 | 修改生成逻辑、调整提示词 |

---

## 4. 配置管理

### 4.1 配置文件位置

**跨平台存储路径**:

- **Windows**: `%APPDATA%/InfinitQuill/config.json`
- **macOS**: `~/Library/Preferences/InfinitQuill/config.json`
- **Linux**: `~/.config/InfinitQuill/config.json`

**首次启动**: 如果用户配置不存在，自动从项目根目录复制`config.json`。

### 4.2 修改配置结构

如果需要添加新配置项，请遵循以下步骤：

```python
# 在 config_manager.py 的 create_config() 函数中

def create_config(config_file: str) -> dict:
    config = {
        # 现有配置...
        "your_new_section": {
            "your_setting": "default_value",
            # 添加你的新配置
        }
    }
```

**重要**: 修改配置结构后，请更新以下位置：
- `config_manager.py`: `create_config()`函数
- `config_widget.py`: UI界面显示新配置

### 4.3 配置示例

查看项目根目录的`config.json`以了解完整配置结构：

```json
{
  "llm_configs": {
    "DeepSeek V3": {
      "api_key": "",
      "base_url": "https://api.deepseek.com/v1",
      "model_name": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 8192,
      "timeout": 600,
      "interface_format": "OpenAI"
    }
  },
  "choose_configs": {
    "prompt_draft_llm": "DeepSeek V3",
    "chapter_outline_llm": "DeepSeek V3",
    "architecture_llm": "Gemini 2.5 Pro"
  }
}
```

---

## 5. 开发模式运行

### 5.1 标准启动

```bash
# 正常启动（完整GUI）
python main.py
```

### 5.2 调试模式

```bash
# 启用详细日志
python main.py --debug

# 显示性能指标（如渲染时间、LLM响应时间）
python main.py --profile
```

### 5.3 测试特定组件

如果想测试某个组件而不启动完整应用：

```bash
# 在 Python REPL 中测试
python

>>> from config_manager import load_config
>>> config = load_config()
>>> print(f"配置加载成功: {len(config)} 个配置项")

>>> from ui_qt import MainWindow
>>> from PySide6.QtWidgets import QApplication
>>> app = QApplication([])
>>> window = MainWindow()
>>> window.show()
>>> app.exec()
```

---

## 6. 添加新功能

### 6.1 添加新UI组件

假设要添加一个新的Widget（如"大纲编辑器"）：

```bash
# 1. 创建新的widget文件
touch ui_qt/widgets/outline_editor.py
```

```python
# 2. 在 ui_qt/widgets/outline_editor.py 中

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class OutlineEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 添加文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在这里编辑大纲...")
        layout.addWidget(self.text_edit)

        # 加载现有大纲（如果有的话）
        self.load_outline()

    def load_outline(self):
        # 从项目文件加载大纲
        pass

    def save_outline(self):
        # 保存大纲到项目文件
        pass
```

```python
# 3. 在 ui_qt/main_window.py 中集成

from ui_qt.widgets.outline_editor import OutlineEditorWidget

class MainWindow(QMainWindow):
    def __init__(self):
        # ...现有代码...

        # 添加新组件到布局
        self.outline_editor = OutlineEditorWidget()
        self.main_layout.addWidget(self.outline_editor)
```

### 6.2 添加新的AI生成模块

假设要添加新的小说生成步骤（如"人物传记生成"）：

```bash
# 1. 创建新模块
touch novel_generator/character_biography.py
```

```python
# 2. 实现生成逻辑

from llm_adapters import create_llm_adapter
from vectorstore_utils import add_to_vectorstore

class CharacterBiographyGenerator:
    def __init__(self, config, llm_name="default"):
        self.config = config
        self.llm = create_llm_adapter(
            api_key=config["llm_configs"][llm_name]["api_key"],
            base_url=config["llm_configs"][llm_name]["base_url"],
            model_name=config["llm_configs"][llm_name]["model_name"]
        )

    def generate_biography(self, character_info):
        """
        根据角色信息生成人物传记

        Args:
            character_info: 角色基本信息（dict）

        Returns:
            biography: 生成的传记文本
        """
        # 构建提示词
        prompt = f"""
        根据以下角色信息，生成详细的人物传记：

        角色姓名: {character_info['name']}
        角色背景: {character_info['background']}
        角色性格: {character_info['personality']}

        要求：
        1. 包含角色的成长经历
        2. 描述角色的关键人生事件
        3. 体现角色的性格形成过程
        4. 字数约2000-3000字

        人物传记：
        """

        # 调用LLM生成
        biography = self.llm.invoke(prompt)

        # 添加到向量数据库（用于后续检索）
        add_to_vectorstore(
            texts=[biography],
            metadata={"type": "character_biography", "name": character_info['name']}
        )

        return biography
```

```python
# 3. 在 UI 层集成

# 在 ui_qt/widgets/role_manager.py中添加按钮

from novel_generator.character_biography import CharacterBiographyGenerator

class RoleManagerWidget(QWidget):
    def __init__(self, config):
        # ...现有代码...

        # 添加"生成传记"按钮
        self.generate_bio_btn = QPushButton("生成传记")
        self.generate_bio_btn.clicked.connect(self.generate_biography)
        self.layout.addWidget(self.generate_bio_btn)

    def generate_biography(self):
        generator = CharacterBiographyGenerator(self.config)

        # 获取当前选中的角色信息
        current_role = self.get_selected_role()

        # 生成传记
        biography = generator.generate_biography(current_role)

        # 显示或保存
        self.display_biography(biography)
```

---

## 7. LLM适配器扩展

### 7.1 添加新的LLM提供商

如需添加新的LLM提供商（如Anthropic Claude）：

```python
# 在 llm_adapters.py 中

class ClaudeAdapter(LLMAdapter):
    """
    Anthropic Claude API适配器
    """

    def __init__(self, api_key, model_name="claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.anthropic.com"

    def invoke(self, prompt, **kwargs):
        """
        调用Claude API

        Args:
            prompt: 输入提示词
            **kwargs: 额外参数（temperature, max_tokens等）

        Returns:
            response_text: API响应文本
        """
        import requests

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model_name,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7)
        }

        response = requests.post(
            f"{self.base_url}/v1/messages",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"]
        else:
            raise Exception(f"API错误: {response.status_code} - {response.text}")

# 在 create_llm_adapter 函数中添加

def create_llm_adapter(interface_format, **kwargs):
    if interface_format == "Claude":
        return ClaudeAdapter(
            api_key=kwargs.get("api_key"),
            model_name=kwargs.get("model_name")
        )
    # ...其他提供商
```

### 7.2 配置UI支持新提供商

在 `config_widget.py` 中添加新的配置表单。

---

## 8. 调试和测试

### 8.1 使用日志

应用使用Python内置的`logging`模块，支持不同日志级别：

```python
import logging

logger = logging.getLogger(__name__)

# 调试信息
logger.debug("变量值: %s", variable)

# 一般信息
logger.info("操作完成")

# 警告
logger.warning("配置文件未找到，使用默认配置")

# 错误
logger.error("LLM调用失败: %s", error_message, exc_info=True)
```

日志输出到：
- 控制台（`stdout`）
- 文件：`app.log`（项目根目录）

### 8.2 常见问题排查

#### 问题1: PySide6导入错误

```python
# 错误信息
ImportError: No module named 'PySide6'

# 解决方案
pip install PySide6==6.8.0
```

#### 问题2: ChromaDB初始化失败

```python
# 错误信息
ImportError: No module named 'chromadb'

# 解决方案
pip install chromadb==1.0.20
```

#### 问题3: LLM接口调用失败

```python
# 错误信息
APIError: 401 Unauthorized

# 可能原因和解决方案
1. API密钥未设置或无效 → 检查config.json中的api_key
2. Base URL不正确 → 验证LLM提供商的API地址
3. 网络问题 → 检查代理设置（如果使用）
```

#### 问题4: 配置文件权限错误

```python
# 错误信息
PermissionError: [Errno 13] Permission denied: '/path/to/config.json'

# 解决方案
# Windows: 以管理员身份运行终端
# macOS/Linux: 检查~/.config/InfinitQuill/目录权限
```

---

## 9. 性能优化技巧

### 9.1 LLM调用优化

- **批量处理**: 合并多个章节生成请求，减少API调用次数
- **缓存结果**: 对于相同的查询，使用向量数据库缓存结果
- **异步调用**: 使用线程避免阻塞UI

```python
# 异步生成示例
def generate_chapter_async(chapter_num, callback):
    def task():
        try:
            result = chapter_generator.generate(chapter_num)
            callback(result)  # 完成后调用回调
        except Exception as e:
            callback(None, error=e)

    threading.Thread(target=task, daemon=True).start()
```

### 9.2 UI响应优化

- **延迟加载**: 对于大章节列表，使用虚拟化列表只渲染可见项
- **后台加载**: 长时间操作显示进度条或加载动画
- **线程分离**: 所有LLM调用在后台线程执行

### 9.3 内存管理

- **及时清理**: 定期清理ChromaDB中旧的向量记录
- **文件处理**: 使用with语句确保文件正确关闭
- **对象释放**: 及时删除不再使用的大对象

```python
# 确保释放LLM客户端（如果需要）
if hasattr(self.llm, 'close'):
    self.llm.close()
```

---

## 10. 贡献指南

### 10.1 提交Pull Request

1. **Fork项目**到自己的GitHub账户
2. **创建功能分支**: `git checkout -b feature/your-feature-name`
3. **实现功能并测试**: 确保不破坏现有功能
4. **代码格式化**: 运行 `black .` 和 `isort .`
5. **提交 commit**: `git commit -m "feat: 添加XX功能"`
6. **推送到远程**: `git push origin feature/your-feature-name`
7. **创建Pull Request**: 描述功能和测试方法

### 10.2 代码规范

- **缩进**: 4个空格（不使用Tab）
- **行长度**: 建议不超过100字符
- **导入**: 按标准库、第三方库、本地模块分组
- **命名**: 使用snake_case（函数/变量），PascalCase（类）
- **注释**: 复杂逻辑添加注释，公共函数添加docstring

```python
# 好的示例
def generate_chapter(self, chapter_number: int, user_guidance: str = "") -> str:
    """
    生成单个章节内容。

    Args:
        chapter_number: 章节编号（从1开始）
        user_guidance: 用户对生成内容的特殊要求（可选）

    Returns:
        chapter_content: 生成的章节内容（字符串）

    Raises:
        ValueError: 当chapter_number无效时
        APIError: 当LLM调用失败时
    """
    if chapter_number < 1:
        raise ValueError("章节编号必须大于0")

    # 调用LLM生成内容
    content = self.llm.invoke(prompt)

    return content
```

### 10.3 测试要求

对于新功能，建议提供：
- [ ] 单元测试（如果适用）
- [ ] 集成测试步骤
- [ ] 手动验证清单

---

## 11. 工具和脚本

### 11.1 代码统计

```bash
# 统计项目代码行数
find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*" | xargs wc -l | tail -1

# 统计单个模块
find ui_qt -name "*.py" | xargs wc -l | tail -1
find novel_generator -name "*.py" | xargs wc -l | tail -1
```

### 11.2 依赖更新

```bash
# 更新所有依赖到最新版本
pip list --outdated | grep -v '^Package' | awk '{print $1}' | xargs -n1 pip install -U

# 导出更新后的依赖
pip freeze > requirements.txt
```

**注意**: 更新依赖后请全面测试应用，特别是主要功能。

---

## 12. 获取帮助

### 12.1 常见问题

**Q: 如何修改默认的LLM温度参数？**
A: 在 `config_manager.py` 的 `create_config()` 函数中修改默认配置。

**Q: 如何添加新的文件格式导出？**
A: 在 `chapter_editor.py` 的导出功能中添加新的格式处理器。

**Q: 如何调试LLM调用？**
A: 启用调试日志：`python main.py --debug`，查看 `app.log` 文件。

### 12.2 联系支持

- **GitHub Issues**: 报告bug或功能请求
- **项目文档**: 查看README.md了解更多信息

---

**最后更新**: 2025-11-16
**文档版本**: 1.0
**适用版本**: InfiniteQuill v2.0+
