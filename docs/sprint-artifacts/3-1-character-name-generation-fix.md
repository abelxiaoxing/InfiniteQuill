# Story 3.1: 主角名字生成错误修复

Status: ready-for-dev

## Story

**作为** 小说创作者，
**我想要** AI生成的主角名字准确且一致，
**以便** 我的小说角色有可信赖的标识。

## Acceptance Criteria

1. **名字合理性验证** - Given 为小说生成主角名字时, When AI生成角色名字后, Then 名字应该通过合理性验证(包含有效字符、长度适中、符合常规命名习惯), And 不应该包含乱码、特殊符号或不合理字符

2. **角色特征一致性** - Given 角色有预设特征(如性别、年龄、文化背景), When 生成名字时, Then 名字应该与这些特征保持一致(如男性角色有男性化名字), And 不应该出现与角色特征矛盾的名字

3. **跨章节名字一致性** - Given 同一角色在多个章节中出现, When 在不同章节生成内容时, Then 角色名字应该保持一致, And 不应该出现同一角色有多个不同名字的情况

4. **乱码检测和预防** - Given AI生成名字时, When 检测生成结果, Then 如果有乱码或不合理输出, Then 应该触发重新生成或记录警告, And 不应该将乱码名字用于小说内容

5. **名字格式标准化** - Given 成功生成名字后, When 保存和使用名字时, Then 名字应该被格式化为标准格式(去除多余空格、首字母大写等), And 确保在整个应用中显示统一

## Tasks / Subtasks

### 任务1: Prompt模板审查和优化 (AC#1, #2)
- [ ] 在prompt_definitions.py中查找角色生成提示词模板
- [ ] 审查当前提示词的结构和参数
- [ ] 优化提示词使其明确要求合理名字格式
- [ ] 添加角色特征参数(性别、年龄、文化背景)
- [ ] 测试不同提示词版本的名字生成质量
- [ ] 选择最优提示词模板

### 任务2: 名字验证逻辑实现 (AC#1, #4)
- [ ] 在novel_generator/chapter.py中创建validate_character_name()函数
- [ ] 实现字符有效性检查(正则表达式: ^[\u4e00-\u9fa5a-zA-Z\s]+$)
- [ ] 实现长度验证(最小2字符,最大20字符)
- [ ] 实现乱码检测(检查Unicode范围)
- [ ] 实现不合理字符过滤(数字、特殊符号等)
- [ ] 添加测试用例验证验证逻辑

### 任务3: 角色特征一致性检查 (AC#2)
- [ ] 创建check_name_consistency(name, traits)函数
- [ ] 实现性别特征一致性检查(如男性名字不包含'娜'、'丽'等女性化字)
- [ ] 实现文化背景一致性检查(如东方角色有东方风格名字)
- [ ] 实现名字年龄一致性检查(如老年角色名字不含有网络流行语)
- [ ] 如果不一致,触发重新生成或记录警告日志

### 任务4: 跨章节名字一致性保证 (AC#3)
- [ ] 创建character_name_registry字典,保存角色ID到名字的映射
- [ ] 在生成角色时检查registry中是否已有该角色
- [ ] 如果已有,使用registry中保存的名字
- [ ] 如果是新角色,生成名字并保存到registry
- [ ] 在project save/load时持久化和恢复registry
- [ ] 测试多章节名字一致性

### 任务5: 名字格式标准化 (AC#5)
- [ ] 创建normalize_character_name(name)函数
- [ ] 实现去除前后空白
- [ ] 实现去除多余内部空格
- [ ] 实现首字母大写或全名适当格式化
- [ ] 在保存和使用名字前调用标准化
- [ ] 验证标准化后的名字格式统一

### 任务6: 错误处理和重试机制 (AC#1, #4)
- [ ] 在名字生成失败时捕获异常
- [ ] 实现最多3次重试机制
- [ ] 如果3次都失败,返回默认名字"待定角色"并记录警告
- [ ] 在状态栏显示"角色名字生成失败,使用默认名字"消息
- [ ] 在app.log中记录详细错误信息

### 任务7: 集成和端到端测试
- [ ] 在generate_character()或类似函数中集成名字验证
- [ ] 测试完整角色生成流程
- [ ] 生成多章节小说验证名字一致性
- [ ] 测试各种边界情况(特殊字符、极长名字等)
- [ ] 验证与Epic 1配置系统的集成

## Dev Notes

### 相关架构细节

**主要文件位置**:
- `prompt_definitions.py` - 角色生成提示词模板
- `novel_generator/chapter.py` - 章节和角色生成逻辑
- `novel_generator/consistency_checker.py` - 一致性验证(可选增强)
- `project_manager.py` - 角色名字持久化

**技术栈**:
- Python正则表达式 - 名字验证
- Unicode字符范围检测 - 乱码检测
- Python字典 - 角色名字注册表
- JSON序列化 - 持久化角色信息

**架构约束**:
- 必须保持与现有生成流程的兼容性
- 名字验证不应该显著降低生成速度
- 验证失败时提供合理的降级方案(默认名字)
- 记录足够的日志以便调试和优化

### 从Epic 1和2学到的经验

**基础设施利用**:
- Epic 1提供自动保存和状态反馈,可用于名字生成进度显示
- Epic 2优化UI,可以在角色管理器中显示名字验证状态
- StatusBar可以显示"角色名字生成中..."和"角色名字生成完成"

**错误处理模式**:
- 遵循Epic 1的错误处理模式: try-except,状态反馈,日志记录
- 优雅降级原则: 验证失败不影响整体小说生成
- 用户友好的错误消息

**跨模块集成**:
- 角色名字需要在多个地方使用: 生成、保存、显示、验证
- 使用中央registry确保一致性
- 持久化到项目文件

### 笔名和角色名字生成最佳实践

**提示词优化策略**:
```python
# 优化前的提示词可能模糊
"Generate a character name"

# 优化后的提示词明确具体
"Generate a reasonable Chinese character name for a male protagonist aged 25-30, \
from a modern urban background. The name should follow standard Chinese naming \
conventions (1-2 characters for given name). Format: Surname + Given name. \
Example: 李明, 张伟"
```

**验证规则示例**:
```python
def validate_chinese_name(name):
    """验证中文名字合理性"""
    # 长度检查
    if len(name) < 2 or len(name) > 4:
        return False

    # 字符检查(应该包含中文汉字)
    if not re.search(r'[\u4e00-\u9fa5]', name):
        return False

    # 不应该包含数字或特殊符号
    if re.search(r'[0-9@#$%^&*()]', name):
        return False

    return True
```

**一致性保证机制**:
```python
class CharacterNameRegistry:
    def __init__(self):
        self.name_map = {}  # character_id -> name

    def get_or_create_name(self, char_id, traits):
        if char_id in self.name_map:
            return self.name_map[char_id]
        else:
            # 生成新名字
            name = generate_and_validate_name(traits)
            self.name_map[char_id] = name
            return name
```

### 性能考虑

**验证开销控制**:
- 正则表达式预编译
- 简单规则先检查(长度、空值),复杂规则后检查(特征一致性)
- 缓存验证结果避免重复验证

**重试机制**:
- 第一次失败: 立即重试
- 第二次失败: 等待100ms后重试
- 第三次失败: 等待500ms后重试
- 超过3次: 降级为默认名字

### AI提示词Eng技巧

**明确性原则**:
- ❌ "生成一个名字" (模糊)
- ✅ "生成一个符合中国文化的男性名字,25-30岁,2-3个汉字" (具体)

**约束性原则**:
- ❌ 不提格式要求 → AI可能返回"name: 张三, age: 25"这样的格式
- ✅ "只返回名字,不包含其他信息" → 明确输出格式

**上下文原则**:
- 在提示词中包含角色背景信息
- 要求名字与背景一致
- 提供示例帮助AI理解期望输出

## References

**来源文档**:
- Epic 3: AI生成质量增强 [Source: docs/epics.md#Epic-3]
- Story 3.1: 主角名字生成错误修复 [Source: docs/epics.md#Story-3.1]
- 架构决策文档 [Source: docs/bmm-architecture-decisions-2025-11-16.md#需求1]

**相关技术文档**:
- LangChain提示词工程最佳实践
- 正则表达式手册（Python re模块）
- Unicode字符范围和编码
- LLM输出结构化指南

**依赖关系**:
- Epic 2的UI优化（Epic 1已完成）
- Consistency checker基础设施（可选增强）
- Project management系统（角色持久化）

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

Story Context: `/home/abelxiaoxing/work/InfiniteQuill/docs/sprint-artifacts/stories/3-1-character-name-generation-fix.context.xml`

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

### Completion Notes List

- 开始Epic 3: AI生成质量增强的第一个故事
- 聚焦于主角名字生成的准确性和一致性
- 这是用户反馈的核心问题之一
- 名字质量是小说创作体验的关键
- 依赖于Epic 1的配置管理和Epic 2的UI优化

### File List

