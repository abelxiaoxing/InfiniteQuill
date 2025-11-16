# Story 3.2: 章节上下文检索系统实现

Status: ready-for-dev

## Story

**作为** 小说创作者，
**我想要** 新生成的章节与之前章节保持上下文连贯，
**以便** 我的小说故事情节自然流畅。

## Acceptance Criteria

1. **前章节内容检索** - Given 生成第N章内容时(N>1), When 开始检索上下文, Then 应该自动从第N-1章中提取关键内容段落, And 不应该检索不相关章节的内容

2. **向量相似度匹配** - Given 已有前章节内容, When 使用向量检索查找最相关段落时, Then 应该基于内容语义相似度计算匹配分数, And 返回分数最高的前k个段落(默认k=3)

3. **上下文集成到提示词** - Given 已检索到相关的前章节段落, When 构建LLM提示词时, Then 应该将这些段落作为上下文添加到提示词中, And 上下文应该以清晰的格式标注(如"前文相关信息:")

4. **Token限制管理** - Given 检索到的前章节内容, When 添加到提示词时, Then 应该遵守max_context_tokens=2000的限制, And 如果超出限制应该动态调整检索段落数k值或减少每个段落长度

5. **ChromaDB元数据过滤** - Given 使用ChromaDB进行向量检索, When 查询时, Then 应该使用metadata过滤确保只检索相关章节(如chapter_num=N-1), And 不应该跨小说项目检索(使用project_id过滤)

6. **上下文质量评估** - Given 检索结果返回, When 评估检索质量时, Then 检索到的段落应该与当前章节主题相关, And 不应该包含无关或重复信息

## Tasks / Subtasks

### 任务1: ChromaDB集合和元数据准备 (AC#5)
- [ ] 在vectorstore_utils.py中查找现有的ChromaDB集合
- [ ] 验证章节内容是否以带元数据的方式存储
- [ ] 如果缺少,添加metadata字段: chapter_num, project_id, content_type
- [ ] 测试元数据过滤查询
- [ ] 验证不同小说项目的隔离性

### 任务2: 章节摘要向量生成 (AC#2)
- [ ] 集成sentence-transformers库
- [ ] 选择合适的中文文本嵌入模型(e.g., paraphrase-multilingual-MiniLM-L12-v2)
- [ ] 在生成章节后,创建章节摘要或关键段落向量
- [ ] 将向量存储到ChromaDB
- [ ] 验证向量质量和检索效果

### 任务3: 上下文检索函数实现 (AC#1, #2, #5)
- [ ] 在knowledge.py或新文件context_retriever.py中创建retrieve_context()函数
- [ ] 实现基于当前章节的语义向量查询
- [ ] 添加metadata过滤条件(chapter_num=N-1, project_id=current_project)
- [ ] 实现k参数控制(默认值3,可动态调整)
- [ ] 返回最相关的k个段落及其相似度分数

### 任务4: Token限制和动态调整 (AC#4)
- [ ] 计算检索到的段落总token数(使用tiktoken或类似库)
- [ ] 如果超过max_context_tokens(2000),减少k值重新检索
- [ ] 如果仍然超出,对段落进行摘要或截断
- [ ] 确保最终上下文在token限制内
- [ ] 记录实际使用的token数到日志

### 任务5: 提示词构建集成 (AC#3)
- [ ] 在chapter.py的generate_chapter()函数中集成上下文检索
- [ ] 在prompt模板中添加"前文相关信息:"部分
- [ ] 将检索到的段落格式化为清晰的上下文块
- [ ] 确保上下文与当前章节的蓝图信息整合
- [ ] 测试提示词的最终格式

### 任务6: 检索质量评估和调优 (AC#2, #6)
- [ ] 创建测试集: 10-20个章节对,人工标注相关性
- [ ] 运行检索系统,计算recall@k和precision@k
- [ ] 分析检索失败案例,调整嵌入模型或参数
- [ ] 测试不同k值(1, 3, 5)对生成质量的影响
- [ ] 选择最优k值作为默认值

### 任务7: 完整集成和端到端测试
- [ ] 集成所有模块: 向量生成 → 存储 → 检索 → 提示词构建 → 生成
- [ ] 测试生成第2章时是否包含第1章上下文
- [ ] 测试生成第5章时是否包含第4章上下文
- [ ] 验证多章节小说的连贯性提升
- [ ] 性能测试: 上下文检索不应该显著增加生成时间
- [ ] 与Story 3.1的名字一致性机制集成测试

## Dev Notes

### 相关架构细节

**主要文件位置**:
- `novel_generator/knowledge.py` - 知识管理和向量检索
- `novel_generator/chapter.py` - 章节生成主逻辑
- `vectorstore_utils.py` - ChromaDB操作封装
- `novel_generator/prompt_definitions.py` - 提示词模板
- `llm_adapters.py` - LLM适配器层(影响token计算)

**技术栈**:
- ChromaDB 1.0.20 - 向量数据库
- sentence-transformers - 多语言文本嵌入
- tiktoken或类似库 - token计数
- OpenAI或其他LLM API - 生成章节内容

**架构约束**:
- 向量检索不应该阻塞主生成流程
- 上下文应该作为可选增强,不应该降低无上下文时的质量
- 需要处理第一个章节(无前文)的边界情况
- 跨项目隔离: 不应该检索其他小说项目的内容

### 关键设计决策

**嵌入模型选择**:
- **选项1**: paraphrase-multilingual-MiniLM-L12-v2
  - 优点: 多语言支持,模型小(110MB),速度快
  - 缺点: 中文语义理解可能不如专用模型
- **选项2**: text2vec-large-chinese
  - 优点: 专门针对中文优化,语义理解更准确
  - 缺点: 模型大(1.3GB),速度慢,GPU内存需求高
- **推荐**: 选项1,平衡性能和效果

**向量存储策略**:
```python
# 存储结构示例
{
    "documents": ["章节1内容", "章节2内容", ...],
    "metadatas": [
        {"chapter_num": 1, "project_id": "project_123", "content_type": "full"},
        {"chapter_num": 2, "project_id": "project_123", "content_type": "full"},
        ...
    ],
    "ids": ["chap_1", "chap_2", ...]
}
```

**上下文格式化**:
```python
# 最佳格式: 清晰的标题和段落
context_formatted = """
前文相关信息:

[片段1](相似度: 0.85)
前文内容中关于主角的背景介绍...

[片段2](相似度: 0.78)
前文情节中的关键事件...

"""
```

**Token限制策略**:
1. 优先减少k值(从默认3降到2,再到1)
2. 如果仍超出限制,对段落进行摘要(使用LLM或提取关键句)
3. 最后手段: 截断段落末尾

### 从Story 3.1学到的经验

**AI生成的质量控制**:
- Story 3.1关注名字生成质量
- Story 3.2关注上下文相关性
- 两者都使用验证和一致性机制

**可复用的模式**:
- 验证机制(S3.1)可以应用于上下文相关性检查(S3.2 AC#6)
- 重试和降级策略(S3.1)可以应用于检索失败(S3.2)
- 状态反馈(S3.1)可以显示"正在检索前文..."和"上下文已加载"

**集成点**:
- Story 3.1确保名字一致性
- Story 3.2确保情节连贯性
- 两者共同提升多章节小说的整体质量

### 性能优化策略

**检索优化**:
- 预计算和缓存章节向量(生成时立即计算)
- 使用HNSW索引加速近似最近邻搜索
- 批量检索多个段落减少数据库查询

**Token计算优化**:
- 缓存token计数结果
- 使用近似算法(对中文按字符数*1.5估算)

**提示词优化**:
- 只将最相关的1-2个段落放入主要提示词
- 其他段落放入次要上下文或脚注

### 边界情况处理

**第一个章节**:
```python
if chapter_num == 1:
    # 没有前文,跳过上下文检索
    context = ""
else:
    context = retrieve_context(chapter_num - 1)
```

**短章节或内容不足**:
- 如果前章节内容太少(k个段落加起来<100字),扩大检索范围
- 考虑使用更早的章节内容作为补充

**检索结果不相关**:
- 如果最高相似度分数<0.6,提示用户或跳过上下文
- 添加日志记录低质量检索结果用于调优

**Token限制非常严格**:
- 如果即使在k=1时也超出token限制,放弃上下文检索
- 确保基本功能不受影响

### 测试和质量保证

**单元测试重点**:
- 向量相似度计算准确性
- metadata过滤正确性
- token计数准确性
- 动态k值调整逻辑

**集成测试重点**:
- 完整流程: 生成→存储→检索→生成
- 跨章节连贯性评估
- Token限制边界测试
- 多项目隔离测试

**人工评估**:
- 生成5-10章的小说样本
- 对比有无上下文的生成质量
- 评估连贯性和一致性提升

### 与LLM API集成考虑

**Token计算**:
- OpenAI API: 使用tiktoken精确计算
- 其他API: 使用近似算法
- 上下文token数 + 蓝图token数 + 生成指令token数 < 模型最大限制

**模型选择**:
- GPT-4: 更强的上下文理解能力
- GPT-3.5-turbo: 成本更低
- 考虑使用config_manager中的API配置

**提示词最佳实践**:
```python
# 优化的提示词结构
prompt = f"""
前文信息:
{context}

当前章节大纲:
{blueprint}

基于以上信息,生成第{chapter_num}章内容。
要求:
1. 情节自然延续前文
2. 保持角色一致性
3. 符合故事整体风格和基调

章节内容:
"""
```

### 与Epic 1和2的集成

**配置管理**:
- 使用Story 1.2的自动保存机制保存上下文检索设置(k值、模型选择等)
- 使用Story 1.3的状态反馈显示"正在检索前文..."

**UI交互**:
- 在Story 2.1简化后的配置界面中添加上下文检索开关
- 在Story 2.3的主题一致性验证中包含上下文显示样式

**质量保证**:
- 遵循Story 1.4的错误处理模式
- 记录详细的debug日志便于问题排查

## References

**来源文档**:
- Epic 3: AI生成质量增强 [Source: docs/epics.md#Epic-3]
- Story 3.2: 章节上下文检索系统实现 [Source: docs/epics.md#Story-3.2]
- 架构决策文档 [Source: docs/bmm-architecture-decisions-2025-11-16.md#需求2]

**相关技术文档**:
- ChromaDB官方文档(metadata过滤)
- sentence-transformers文档
- LangChain向量存储集成
- OpenAI API token计算
- LLM提示词工程最佳实践

**依赖关系**:
- Story 3.1完成(角色名字一致性)
- ChromaDB向量数据库可用
- sentence-transformers模型下载和加载

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->
/home/abelxiaoxing/work/InfiniteQuill/docs/sprint-artifacts/stories/3-2-chapter-context-retrieval-system.context.xml

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

### Completion Notes List

- 开始Epic 3的第二个故事,关注章节上下文连贯性
- 使用向量检索技术增强AI生成质量
- 与Story 3.1的名字一致性机制协同工作
- 显著提升多章节小说的连贯性和质量
- 依赖于ChromaDB和sentence-transformers技术栈

### File List

