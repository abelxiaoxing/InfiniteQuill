# Story 2.2: 暗色主题角色列表样式修复

Status: ready-for-dev

## Story

**作为** 使用暗色模式的用户，
**我想要** 角色列表的选中项有合适的颜色，
**以便** 在夜间模式下能够清晰地看到选中的角色。

## Acceptance Criteria

1. **选中项背景色** - Given 应用处于暗色模式, When 从角色列表中选择任意角色时, Then 选中项的背景颜色应该显示为暗灰色(#3a3a3a), And 与周围项有足够的视觉区分

2. **选中项文字色** - Given 角色项已被选中, When 查看角色名字和详情文字时, Then 文字颜色应该为纯白色(#ffffff), 确保最佳的对比度和可读性

3. **悬停状态反馈** - Given 鼠标悬停在角色列表项上(无论是否选中), When 悬停时, Then 该项的背景色应该变为稍亮的灰色(#4a4a4a), And 应该有清晰的视觉反馈表明该项可交互

4. **WCAG对比度合规** - Given 选中项显示暗灰色背景(#3a3a3a)和白色文字(#ffffff), When 计算对比度比例时, Then 应该满足WCAG 2.1 AA标准(至少4.5:1), 确保色盲用户也能清晰辨认

5. **主题整体协调性** - Given 暗色模式全局应用, When 查看角色管理器所有UI元素时, Then 角色列表的选中样式应该与工具栏、按钮等其他暗色元素协调一致, 不应该出现突兀的视觉风格

## Tasks / Subtasks

### 任务1: 控件类型识别和样式分析 (AC#1, #3, #5)
- [ ] 在role_manager.py中查找角色列表控件类型(QListWidget或QTableView)
- [ ] 检查material_dark.qss文件中现有的列表项样式
- [ ] 分析当前选中项的样式问题(白底白字)
- [ ] 识别需要修改的QSS选择器
- [ ] 测试悬停状态的现有实现

### 任务2: QSS样式规则实现 (AC#1, #2, #3)
- [ ] 在material_dark.qss中添加QListWidget::item:selected规则
- [ ] 设置背景色为#3a3a3a
- [ ] 设置文字颜色为#ffffff
- [ ] 添加QListWidget::item:selected:hover规则(背景#4a4a4a)
- [ ] 添加QListWidget::item:hover规则(悬停效果)
- [ ] 如果是QTableView,添加对应的::item:selected和::item:hover规则
- [ ] 移除或覆盖原有的白底样式

### 任务3: WCAG对比度验证 (AC#4)
- [ ] 使用对比度检测工具验证#3a3a3a与#ffffff的对比度
- [ ] 确保比例≥4.5:1
- [ ] 测试在不同显示器和亮度设置下的可读性
- [ ] 如果对比度不足,调整颜色值并重新验证

### 任务4: 跨主题兼容性测试 (AC#5)
- [ ] 切换到浅色模式,验证没有样式冲突
- [ ] 确保material_light.qss不受暗色样式影响
- [ ] 测试在两种主题间切换时的平滑过渡
- [ ] 验证角色管理器内其他控件(按钮、输入框等)的样式一致性

### 任务5: 视觉回归测试 (AC#1-#5)
- [ ] 截取暗色模式下角色列表的截图
- [ ] 验证选中项视觉样式符合设计
- [ ] 测试不同角色数量下的显示效果
- [ ] 验证滚动时选中项样式保持一致
- [ ] 测试选中多个角色时的样式显示

### 任务6: 代码整理和文档化
- [ ] 在QSS文件中添加注释说明样式规则用途
- [ ] 更新相关文档(如style guide)
- [ ] 记录颜色值和设计决策
- [ ] 代码审查和格式化

## Dev Notes

### 相关架构细节

**主要文件位置**:
- `ui_qt/widgets/role_manager.py` - 角色管理器主组件
- `ui_qt/styles/material_dark.qss` - 暗色主题样式表
- `ui_qt/styles/material_light.qss` - 浅色主题样式表(需要确保不受影响)
- `ui_qt/utils/theme_manager.py` - 主题加载和管理

**技术栈**:
- PySide6 6.8.0 - Qt框架
- QSS(Qt Style Sheets) - 样式规则
- QListWidget或QTableView - 列表控件

**架构约束**:
- 必须保持与浅色模式的样式隔离
- 遵循Material Design暗色模式规范
- 确保悬停和选中状态有视觉层次
- 不影响其他暗色主题元素的样式

### Design Considerations

**颜色选择原理**:
- **#3a3a3a (选中背景)**: 暗灰色,足够暗以突出选中,但比纯黑(#000000)柔和
- **#ffffff (文字)**: 纯白色,确保最大对比度和可读性
- **#4a4a4a (悬停)**: 比选中色稍亮,提供微妙但可感知的悬停反馈

**视觉层次**:
```
普通项: 背景#2d2d2d → 悬停#4a4a4a → 选中#3a3a3a
层级:   基础层    → 交互反馈层   → 激活状态层
```

**WCAG 2.1 AA标准**:
- 对比度计算公式: (L1 + 0.05) / (L2 + 0.05)
- #3a3a3a亮度: ~0.15
- #ffffff亮度: ~1.0
- 对比度: (1.0 + 0.05) / (0.15 + 0.05) = 5.25:1 ✅ (大于4.5:1要求)

### 从Story 2.1和Epic 1学到的经验

**UI简化经验**:
- Story 2.1移除了一个不必要的配置选项
- UI简化后,Story 2.2优化剩余的UI元素
- 两者都提升了用户体验,减少认知负担

**配置基础设施重复利用**:
- Epic 1的自动保存确保样式变更立即持久化
- UI改动后可以自动生效无需用户手动保存
- StatusBar可以显示"主题已更新"反馈

**跨故事一致性**:
- 颜色方案应该与StatusBar的信息/成功/错误状态协调
- Material Design规范确保整体一致性
- 用户在不同功能模块间体验一致

### 潜在问题和缓解措施

**风险1: 颜色与其他元素冲突**
- **缓解**: 在暗色主题全局视图中检查,确保颜色协调
- **测试**: 截图对比整体UI,确保没有突兀的元素

**风险2: 不同Qt版本样式差异**
- **缓解**: 在PySide6 6.8.0上充分测试
- **测试**: 检查QListWidget和QTableView的样式行为一致性

**风险3: 高DPI显示器显示问题**
- **缓解**: 使用相对颜色而非固定像素
- **测试**: 在1080p和4K显示器上测试

## References

**来源文档**:
- Epic 2: UI/UX体验优化 [Source: docs/epics.md#Epic-2]
- Story 2.2: 暗色主题角色列表样式修复 [Source: docs/epics.md#Story-2.2]

**相关技术文档**:
- 架构决策文档 [Source: docs/bmm-architecture-decisions-2025-11-16.md#需求4]
- QSS样式表文档: Qt Style Sheets Reference
- Material Design暗色模式规范
- WCAG 2.1对比度指南
- PySide6 QListWidget和QTableView文档

**Story 2.1依赖**:
- Story 2.1完成(UI简化,移除详细程度选项)
- Epic 1配置自动保存(确保样式变更自动持久化)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

### Completion Notes List

- 开始Epic 2的第二个故事,关注暗色主题优化
- 依赖于Story 2.1的UI简化成果
- 直接响应用户反馈(白底白字问题)
- 提升暗色模式的可用性和美观度
- 符合Material Design和WCAG标准

### File List

