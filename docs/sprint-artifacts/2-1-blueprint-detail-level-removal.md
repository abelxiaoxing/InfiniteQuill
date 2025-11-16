# Story 2.1: 章节蓝图详细程度选项移除

Status: ready-for-dev

## Story

**作为** 最终用户，
**我想要** 简化章节蓝图生成界面，
**以便** 无需选择详细程度就能获得最佳的生成质量。

## Acceptance Criteria

1. **UI控件移除** - Given 用户在章节蓝图生成界面, When 查看所有配置控件时, Then 不应该看到详细程度选择下拉框, And UI布局应该自动调整填补空白

2. **默认详细模式** - Given 用户触发蓝图生成, When 调用blueprint.py的生成函数时, Then detail_level参数应该固定为"detailed", And 不应该接受其他详细程度值

3. **配置文件清理** - Given 检查配置文件config.json, When 查找blueprint_detail_level设置时, Then 不应该存在该配置项, And 如果存在旧值应该被安全移除

4. **生成质量验证** - Given 使用详细模式生成蓝图, When 检查生成的内容时, Then 蓝图长度应该大于500字符, And 内容应该包含足够的细节信息, And 不应该出现"简要"或"标准"等简略内容

5. **向后兼容性** - Given 加载旧版本的配置文件(包含blueprint_detail_level), When 应用启动时, Then 应该忽略该设置而不报错, And 应该使用详细模式作为默认行为

## Tasks / Subtasks

### 任务1: UI控件识别和移除 (AC#1)
- [ ] 在config_widget.py中定位详细程度选择控件(查找combo box、select或dropdown)
- [ ] 识别控件的变量名和初始化代码
- [ ] 识别控件的布局位置(layout.addWidget等)
- [ ] 移除控件初始化代码
- [ ] 移除控件添加到布局的代码
- [ ] 测试UI布局自动调整

### 任务2: 蓝图生成逻辑修改 (AC#2, #4)
- [ ] 在blueprint.py中查找generate_blueprint()函数
- [ ] 定位detail_level参数
- [ ] 移除detail_level参数(如果存在)
- [ ] 在函数内部固定设置detail_level = "detailed"
- [ ] 验证生成的蓝图内容长度和质量
- [ ] 测试简要/标准模式不会被使用

### 任务3: 配置文件处理 (AC#3, #5)
- [ ] 在config_manager.py中查找配置加载逻辑
- [ ] 添加对blueprint_detail_level的忽略逻辑(如果存在)
- [ ] 记录警告日志提示旧配置项被忽略
- [ ] 测试加载包含旧配置项的文件
- [ ] 验证应用正常启动不报错
- [ ] 测试新生成的配置文件不包含该设置

### 任务4: UI布局重新组织 (AC#1)
- [ ] 在config_widget.py的blueprint配置区域重新布局
- [ ] 移除详细程度相关的label和说明文字
- [ ] 调整其他控件的间距和位置
- [ ] 验证整体UI美观性和一致性
- [ ] 在不同窗口尺寸下测试布局

### 任务5: 代码清理和文档更新 (AC#3, #5)
- [ ] 搜索整个代码库中blueprint_detail_level的引用
- [ ] 移除所有相关常量、枚举或类型定义
- [ ] 更新相关文档字符串和注释
- [ ] 检查用户文档(README等)并更新说明
- [ ] 更新变更日志或发行说明

### 任务6: 测试和验证
- [ ] 单元测试: verify UI控件已移除
- [ ] 集成测试: verify 蓝图始终使用详细模式
- [ ] 回归测试: verify 旧配置文件兼容性
- [ ] 手动测试: 验证UI布局正常
- [ ] 性能测试: verify 生成质量(详细模式)

## Dev Notes

### 相关架构细节

**主要文件位置**:
- `ui_qt/widgets/config_widget.py` - UI控件和布局
- `novel_generator/blueprint.py` - 蓝图生成逻辑
- `config_manager.py` - 配置加载和保存

**技术栈**:
- PySide6 6.8.0 - Qt UI控件移除和布局调整
- JSON配置管理

**架构约束**:
- 旧配置文件必须向后兼容
- UI变更应该不影响其他配置功能
- 移除后确保没有代码残留

### 设计考虑

**简化决策理由**:
- 小说生成需要高质量内容，详细模式最有价值
- 减少用户选择负担，提供最佳默认体验
- 符合AI文学创作的专业需求

**向后兼容策略**:
- 静默忽略旧配置项(不抛错，记录日志)
- 不着删除用户配置文件(只忽略特定设置)
- 逐步迁移，不影响现有用户

### 从Epic 1学到的经验

**基础设施准备**:
- Epic 1 (配置自动保存)提供稳定的基础设施
- 配置文件管理更加健壮
- 错误处理机制已建立

**可复用的模式**:
- config_manager.py中的配置管理模式
- 用户友好的错误消息显示
- UI变更的平滑过渡

**UI变更注意事项**:
- 布局调整可能影响窗口大小
- 需要测试不同分辨率下的显示
- 确保与其他控件的间距合理

### 实施顺序注意事项

**前提条件**: Epic 1完成(配置自动保存功能)
**理由**:
- 配置改动可以自动保存(Story 1.1-1.4)
- UI移除操作后配置立即保存
- 提供更好的用户体验

## References

**来源文档**:
- Epic 2: UI/UX体验优化 [Source: docs/epics.md#Epic-2]
- Story 2.1: 章节蓝图详细程度选项移除 [Source: docs/epics.md#Story-2.1]

**相关技术文档**:
- 架构决策文档 [Source: docs/bmm-architecture-decisions-2025-11-16.md#需求3]
- PySide6 UI控件文档: QComboBox, QLabel, QLayout
- Configuration management patterns from Story 1.1-1.4

**依赖配置**:
- 无特殊依赖，属于纯UI和配置逻辑改动
- 需要Epic 1的配置自动保存基础设施

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->
- `/home/abelxiaoxing/work/InfiniteQuill/docs/sprint-artifacts/stories/2-1-blueprint-detail-level-removal.context.xml`

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

### Completion Notes List

- 开始Epic 2: UI/UX体验优化的第一个故事
- 简化了用户界面，消除不必要的配置选项
- 依赖于Epic 1的配置基础设施
- 故事2.1关注UI简化，为后续UI改进奠定基础

### File List

