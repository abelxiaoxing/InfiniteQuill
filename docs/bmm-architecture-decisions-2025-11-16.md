# InfiniteQuill - 架构决策文档

**项目**: InfiniteQuill - AI小说生成器增强
**文档类型**: 架构决策和实现指导
**创建日期**: 2025-11-16
**目标**: 指导AI代理实施5个功能增强和bug修复

---

## 1. 执行摘要

本文档为InfiniteQuill项目的5个功能增强和bug修复提供架构决策和实现指导。项目是一个13,355行的Python桌面应用，采用模块化架构（UI层 + AI生成层）。

**本次改动目标**:
1. 修复主角名字生成错误
2. 增强章节上下文连贯性
3. 修复章节蓝图详细程度选项bug
4. 优化UI暗色模式角色列表颜色
5. 实现配置管理的无感自动保存

---

## 2. 需求架构映射

### 2.1 需求1: 修复主角名字生成错误

**问题描述**: 在生成小说主角名字时，有时会出现错误或不一致的名字。

**影响范围分析**:
- **主要模块**: `novel_generator/chapter.py`
- **相关文件**: `prompt_definitions.py` (提示词模板)
- **可能涉及**: `consistency_checker.py` (一致性检查逻辑)

**架构决策**:
- **根本原因**: 提示词模板可能未正确传递角色参数，或LLM理解有歧义
- **解决方案**:
  1. 审查 `prompt_definitions.py` 中的角色生成提示词
  2. 在 `novel_generator/chapter.py` 中添加角色名字验证逻辑
  3. 如有必要，增强一致性检查器验证角色名字连贯性

**实现指导**:
```python
# 在 chapter.py 的生成函数中添加:
def validate_character_name(name, expected_traits):
    """验证生成的角色名字是否符合预期特征"""
    # 检查名字合理性
    # 如果不符合，重新生成或记录警告
```

**测试策略**:
- 单元测试: 验证名字生成函数输出一致性
- 集成测试: 完整章节生成流程验证角色名字正确性

---

### 2.2 需求2: 增强章节上下文连贯性

**问题描述**: 章节生成时只依赖大纲和蓝图，缺乏与之前章节的上下文联系。

**影响范围分析**:
- **主要模块**: `novel_generator/chapter.py` (章节内容生成)
- **关键文件**: `knowledge.py` (知识管理 - 向量检索)
- **相关文件**: `vectorstore_utils.py` (ChromaDB操作)

**架构决策**:
- **当前状态**: 已有基础向量检索实现，但检索范围和上下文提取需要优化
- **增强方案**:
  1. 在生成第N章时，自动检索第N-1章的关键内容（通过向量相似度）
  2. 将前章节摘要作为上下文添加到提示词中
  3. 使用ChromaDB的metadata过滤，确保只检索相关章节

**实现指导**:
```python
# 在 chapter.py 中增强上下文检索:
def generate_chapter_with_context(chapter_num, blueprint, previous_chapters):
    """生成章节时包含前章节上下文"""
    if chapter_num > 1:
        # 检索前章节内容
        context = retrieve_relevant_context(
            current_chapter=blueprint[chapter_num],
            previous_chapters=previous_chapters,
            k=3  # 检索前3个最相关段落
        )
        # 将context添加到LLM提示词
        prompt = build_prompt_with_context(blueprint, context)
```

**技术要点**:
- 使用 `sentence-transformers` 生成章节摘要向量
- 通过ChromaDB检索最相关的前章节段落
- 平衡上下文长度（避免提示词过长）

---

### 2.3 需求3: 修复章节蓝图详细程度选项Bug

**问题描述**: 生成章节蓝图时，详细程度选项设置无效，需要默认为详细配置。

**影响范围分析**:
- **主要模块**: `novel_generator/blueprint.py`
- **配置处理**: `config_manager.py` (如果配置未正确传递)
- **UI组件**: `ui_qt/widgets/config_widget.py` (详细程度设置界面)

**架构决策**:
- **策略**: **移除详细程度选项**，固定使用详细模式
- **理由**: 小说生成场景需要高质量详细内容，简要和标准模式价值有限

**实现指导**:

**步骤1**: 从UI中移除详细程度选择控件
```python
# 在 config_widget.py 中:
# 移除或注释掉详细程度选择下拉框
# self.detail_level_combo = QComboBox()
```

**步骤2**: 在blueprint.py中移除详细程度参数
```python
# 在 blueprint.py 的 generate_blueprint() 函数中:
# 移除 detail_level 参数
# 固定使用详细模式:
detail_level = "detailed"  # 固定值
```

**步骤3**: 清理配置文件的详细程度设置
```python
# 在 config.json 中移除:
# "blueprint_detail_level": "standard"
```

**测试策略**:
- 验证UI不再显示详细程度选项
- 验证所有蓝图生成都使用详细模式
- 验证输出内容质量符合预期

---

### 2.4 需求4: UI暗色模式角色列表颜色优化

**问题描述**: 暗色模式下角色列表选中项太亮，白底白字不符合夜间模式视觉体验。

**影响范围分析**:
- **主题样式**: `ui_qt/styles/material_dark.qss` (深色主题QSS文件)
- **主题管理**: `ui_qt/utils/theme_manager.py`
- **相关Widget**: `ui_qt/widgets/role_manager.py` (角色管理器)

**架构决策**:
- **问题原因**: QSS样式表中角色列表的选中状态颜色配置不当
- **解决方案**: 调整暗色主题中QListWidget或QTableView的选中项颜色

**实现指导**:

**步骤1**: 定位角色列表控件类型
```python
# 在 role_manager.py 中查找:
# self.role_list = QListWidget() 或 QTableView
```

**步骤2**: 修改material_dark.qss样式
```qss
/* 在 ui_qt/styles/material_dark.qss 中添加/修改: */

QListWidget::item:selected {
    background-color: #3a3a3a;  /* 暗色选中背景 */
    color: #ffffff;              /* 白色文字 */
    border: none;
}

QListWidget::item:selected:hover {
    background-color: #4a4a4a;  /* 悬停时的稍亮背景 */
}

/* 如果是QTableView: */
QTableView::item:selected {
    background-color: #3a3a3a;
    color: #ffffff;
}
```

**步骤3**: 验证对比度
- 确保选中项背景与文字有足够的对比度 (WCAG AA标准: 4.5:1)
- 在暗色背景下测试可读性

**视觉测试清单**:
- [ ] 选中项背景为暗灰色 (#3a3a3a)
- [ ] 文字为纯白色 (#ffffff)
- [ ] 悬停状态有视觉反馈
- [ ] 与整体暗色主题协调

---

### 2.5 需求5: 配置管理无感（自动保存）

**问题描述**: 配置修改后需要自动应用并保存，无需用户手动操作。

**影响范围分析**:
- **主要模块**: `config_manager.py` (配置保存逻辑)
- **UI组件**: `ui_qt/widgets/config_widget.py` (配置变更监听)
- **状态反馈**: `ui_qt/widgets/status_bar.py` (保存状态提示)

**架构决策**:
- **策略**: 延迟自动保存 (2秒延迟)
- **理由**: 平衡用户体验和性能，避免频繁I/O操作

**实现指导**:

**步骤1**: 在config_widget.py中添加变更监听
```python
from PySide6.QtCore import QTimer

class ConfigWidget(QWidget):
    def __init__(self):
        # ...现有代码...
        self.save_timer = QTimer()
        self.save_timer.setInterval(2000)  # 2秒延迟
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save_config)

    def on_config_changed(self, key, value):
        """配置变更时触发"""
        # 更新内存中的配置
        self.config[key] = value
        # 重置并启动定时器
        self.save_timer.stop()
        self.save_timer.start()
        # 显示待保存状态
        self.show_save_pending()
```

**步骤2**: 实现自动保存功能
```python
def auto_save_config(self):
    """自动保存配置到文件"""
    try:
        from config_manager import save_config
        success = save_config(self.config)
        if success:
            self.show_save_success()
        else:
            self.show_save_error()
    except Exception as e:
        logging.error(f"自动保存配置失败: {e}")
        self.show_save_error()
```

**步骤3**: 添加UI状态反馈
```python
def show_save_pending(self):
    """显示保存待处理状态"""
    self.status_bar.set_info_state("配置已更改，2秒后自动保存...")

def show_save_success(self):
    """显示保存成功"""
    self.status_bar.set_success_state("配置已自动保存")
    # 3秒后清除状态
    QTimer.singleShot(3000, lambda: self.status_bar.clear_status())

def show_save_error(self):
    """显示保存错误"""
    self.status_bar.set_error_state("配置保存失败，请重试")
```

**步骤4**: 处理边界情况
```python
def closeEvent(self, event):
    """窗口关闭时确保保存"""
    if self.save_timer.isActive():
        # 立即保存
        self.auto_save_config()
    event.accept()
```

**性能考虑**:
- 2秒延迟避免快速连续修改时的重复保存
- 使用QTimer实现非阻塞延迟
- 文件I/O在后台线程执行（避免UI卡顿）

---

## 3. 实现模式（AI代理一致性规则）

### 3.1 代码组织模式

**文件命名约定**:
- Python模块: snake_case (`user_manager.py`)
- 类名: PascalCase (`UserManager`)
- 函数名: snake_case (`get_user_data()`)

**目录结构**:
```
修改的文件位置:
├── ui_qt/
│   ├── widgets/config_widget.py        # 配置自动保存 + 移除详细程度选项
│   ├── widgets/role_manager.py         # 暗色模式样式应用
│   └── utils/theme_manager.py          # 主题加载
├── novel_generator/
│   ├── chapter.py                      # 名字生成修复 + 上下文增强
│   ├── blueprint.py                    # 详细程度选项移除
│   └── consistency_checker.py          # 一致性增强
└── config_manager.py                   # 配置保存逻辑
```

### 3.2 错误处理模式

**所有模块统一使用**:
```python
try:
    # 主要逻辑
    result = perform_action()
    return result
except SpecificError as e:
    logging.error(f"具体错误: {e}", exc_info=True)
    return None 或 默认值
except Exception as e:
    logging.exception(f"意外错误: {e}")
    # 用户友好的错误消息
    return error_response("操作失败，请重试")
```

**示例（配置自动保存）**:
```python
def auto_save_config(self):
    try:
        from config_manager import save_config
        success = save_config(self.config)
        if not success:
            raise Exception("保存函数返回False")
        return True
    except Exception as e:
        logging.error(f"自动保存配置失败: {e}")
        self.status_bar.set_error_state("配置保存失败")
        return False
```

### 3.3 日志记录模式

**统一日志格式**:
```python
import logging

logger = logging.getLogger(__name__)

# 信息日志
logger.info(f"正在生成分布要求蓝图的第 {chapter_num} 章")

# 调试日志
logger.debug(f"配置变更: {key} = {value}")

# 错误日志（带堆栈）
logger.exception(f"章节生成失败: {error}")

# 带数据日志
logger.info(f"配置已保存: 共 {len(config)} 个设置项")
```

**日志级别使用**:
- `INFO`: 主要业务操作（生成、保存、配置变更）
- `DEBUG`: 详细调试信息（函数参数、中间结果）
- `WARNING`: 非致命问题（配置缺失但使用默认值）
- `ERROR`: 可恢复的错误（保存失败、API超时）
- `CRITICAL`: 致命错误（应用无法继续运行）

### 3.4 状态反馈模式

**状态栏使用统一模式**:
```python
# 操作进行中
self.status_bar.set_info_state("正在保存配置...")

# 操作成功
self.status_bar.set_success_state("配置已保存")
QTimer.singleShot(3000, lambda: self.status_bar.clear_status())

# 操作警告
self.status_bar.set_warning_state("配置部分保存成功，部分项目失败")

# 操作错误
self.status_bar.set_error_state("配置保存失败: 权限不足")
```

**状态持续时间**:
- 成功消息: 显示3秒后自动清除
- 错误消息: 显示直到用户操作或手动清除
- 进行消息: 操作完成后更新

---

## 4. 测试策略

### 4.1 单元测试清单

**需求1: 名字生成修复**
```python
def test_character_name_generation():
    """测试角色名字生成逻辑"""
    # 设置测试数据
    chapter_gen = ChapterGenerator(config)

    # 生成名字
    name = chapter_gen.generate_character_name(traits)

    # 验证名字合理性
    assert name is not None
    assert len(name) > 0
    assert name.isprintable()
```

**需求2: 上下文连贯性**
```python
def test_cross_chapter_context_retrieval():
    """测试跨章节上下文检索"""
    # 准备前章节内容
    previous_chapters = load_test_chapters()

    # 检索相关上下文
    context = retrieve_context(current_chapter, previous_chapters, k=3)

    # 验证检索到内容
    assert len(context) > 0
    assert context.is_relevant_to(current_chapter)
```

**需求3: 详细程度移除**
```python
def test_blueprint_always_detailed():
    """验证蓝图生成始终使用详细模式"""
    blueprint = generate_blueprint(chapter_info)

    # 验证输出内容长度（详细模式应更长）
    assert len(blueprint) > 500  # 详细模式应有足够长度
    assert "简要" not in blueprint  # 不应有简要内容
```

**需求4: UI暗色模式颜色**
```python
def test_dark_mode_selection_color():
    """验证暗色模式下选中项颜色"""
    theme_manager.set_theme("dark")

    # 选中项
    role_manager.select_item(0)
    selected_style = role_manager.get_selected_item_style()

    # 验证颜色
    assert selected_style.background_color == "#3a3a3a"
    assert selected_style.text_color == "#ffffff"
```

**需求5: 配置自动保存**
```python
def test_config_auto_save():
    """验证配置自动保存机制"""
    # 修改配置
    config_widget.set_value("api_key", "test_key")

    # 等待2秒
    time.sleep(2.5)

    # 验证配置已保存
    saved_config = load_config()
    assert saved_config["api_key"] == "test_key"
```

### 4.2 集成测试清单

- [ ] 完整章节生成流程（含修复后的名字生成）
- [ ] 多章节生成上下文连贯性验证
- [ ] 主题切换后角色列表颜色正确显示
- [ ] 配置修改自动保存并正确加载
- [ ] UI控件移除详细程度选项后正常操作
- [ ] 错误日志正确显示在状态和日志文件

### 4.3 手动测试清单

**需求1-2: AI生成功能**
- [ ] 生成新小说并验证主角名字正确
- [ ] 生成多章节小说并验证上下文连贯性
- [ ] 切换不同LLM提供商测试名字生成一致性

**需求3: 详细程度移除**
- [ ] 验证UI不再显示详细程度选择
- [ ] 验证所有蓝图生成都使用详细模式
- [ ] 验证配置文件中无详细程度设置

**需求4: UI暗色模式**
- [ ] 切换到暗色模式
- [ ] 在角色管理器中选择角色
- [ ] 验证选中项背景为暗灰色，文字为白色
- [ ] 验证与其他暗色主题元素协调

**需求5: 配置自动保存**
- [ ] 修改API密钥，等待2秒
- [ ] 验证状态栏显示"配置已自动保存"
- [ ] 关闭应用并重新打开
- [ ] 验证配置仍然正确（已持久化）
- [ ] 快速连续修改多个配置项，验证只保存一次

---

## 5. 潜在风险和缓解措施

### 风险1: 上下文检索导致提示词过长

**风险**: 章节上下文增强可能使LLM提示词超出token限制。

**缓解措施**:
- 设置上下文token限制（max_context_tokens=2000）
- 使用摘要而非完整前章节内容
- 动态调整检索段落数（k值）

### 风险2: 频繁自动保存导致性能问题

**风险**: 2秒延迟自动保存可能导致I/O操作过多。

**缓解措施**:
- 配置变更批量处理（2秒延迟已解决）
- 如果性能问题明显，增加延迟至3-5秒
- 监控app.log中的保存操作频率

### 风险3: UI改动破坏主题系统

**风险**: 修改暗色模式样式可能影响Material Design主题一致性。

**缓解措施**:
- 严格按照QSS样式表规范修改
- 在浅色和暗色模式下分别测试
- 保持与其他组件的视觉一致性

### 风险4: 详细程度移除影响现有项目

**风险**: 移除详细程度选项可能影响已有项目配置。

**缓解措施**:
- 向后兼容：忽略配置文件中的详细程度设置
- 迁移脚本（如果需要）：清理旧配置文件
- 文档说明：在README中说明变更

---

## 6. 开发顺序建议

### 推荐实现顺序（按依赖关系）

**阶段1: 基础设施改动（配置管理）**
1. **需求5**: 配置自动保存
   - 为其他配置的自动保存奠定基础
   - 风险低，易于测试

**阶段2: UI改动（主题和选项移除）**
2. **需求4**: 暗色模式颜色优化
   - UI独立改动，不影响其他模块
3. **需求3**: 移除详细程度选项
   - 简化后续开发（无需考虑多个模式）

**阶段3: AI核心改动（生成逻辑）**
4. **需求2**: 章节上下文连贯性增强
   - 中等复杂度，需要充分测试
5. **需求1**: 名字生成错误修复
   - 依赖于上下文检索增强（可以使用相同的基础设施）

**阶段4: 集成测试**
6. 完整小说生成流程测试
7. 所有5个改动的回归测试

---

## 7. 下一步行动

### 立即行动（准备开发）

1. **审查和确认架构决策**
   - 确认5个需求的实现方案
   - 确认一致性模式
   - 确认测试策略

2. **准备开发环境**
   - 确保Python 3.12+环境
   - 安装所有依赖: `pip install -r requirements.txt`
   - 验证应用正常启动

3. **创建开发分支**
   ```bash
   git checkout -b feature/enhancements-phase1
   ```

### 后续行动（开发阶段）

1. **按照推荐顺序实现5个需求**
   - 参考本文档的实现指导
   - 遵循一致性模式
   - 添加单元测试

2. **运行完整测试套件**
   - 单元测试
   - 集成测试
   - 手动UI测试

3. **代码审查和合并**
   - 自我审查
   - 运行black和isort格式化
   - 合并到主分支

---

## 8. 文档信息

**文档创建**: 2025-11-16
**架构师**: Winston (Architect Agent)
**项目**: InfiniteQuill
**代码规模**: 13,355行 (Python)
**技术栈**: PySide6, LangChain, ChromaDB

**相关文档**:
- 项目索引: docs/index.md
- 架构概览: docs/architecture.md
- 组件清单: docs/component-inventory.md
- 开发指南: docs/development-guide.md

**后续文档需要**:
- 技术规范（每个需求的详细技术设计）
- 用户故事和验收标准（SM格式）
- Sprint计划和任务分解

---

**文档状态**: 完成 - 已准备进入开发阶段
