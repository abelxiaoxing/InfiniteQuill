# Story 1.1: Multi-Project System Foundation

Status: ready-for-dev

## Story

As a 开发团队,
I want 建立多项目管理的核心基础设施,
so that 支持用户创建和管理多个小说项目，为后续功能提供可靠的基础平台.

## Acceptance Criteria

1. Given 系统启动时 When 初始化项目管理模块时 Then 应该创建默认的项目数据结构
2. And 应该建立项目配置存储机制
3. And 应该支持项目间的隔离存储
4. And 项目数据结构应该支持：项目元数据（标题、创建时间、最后修改）
5. And 项目数据结构应该支持：角色数据存储
6. And 项目数据结构应该支持：生成内容存储
7. And 项目数据结构应该支持：配置设置存储

## Tasks / Subtasks

- [ ] 任务1: 核心数据结构设计 (AC: 1, 4, 5, 6, 7)
  - [ ] 子任务1.1: 创建Project类定义项目属性
  - [ ] 子任务1.2: 实现项目元数据字段（标题、创建时间、最后修改）
  - [ ] 子任务1.3: 设计角色数据存储结构
  - [ ] 子任务1.4: 设计生成内容存储结构
  - [ ] 子任务1.5: 设计配置设置存储结构
- [ ] 任务2: 存储机制实现 (AC: 2, 3)
  - [ ] 子任务2.1: 扩展hybrid_data_manager.py支持项目隔离
  - [ ] 子任务2.2: 实现项目配置的SQLite存储
  - [ ] 子任务2.3: 实现大容量数据的文件系统存储
  - [ ] 子任务2.4: 确保项目间数据隔离
- [ ] 任务3: 项目管理器增强 (AC: 1)
  - [ ] 子任务3.1: 实现项目初始化逻辑
  - [ ] 子任务3.2: 添加默认项目创建功能
  - [ ] 子任务3.3: 集成混合数据管理器
  - [ ] 子任务3.4: 实现项目ID生成机制
- [ ] 任务4: 测试和验证 (AC: 全部)
  - [ ] 子任务4.1: 测试项目数据模型
  - [ ] 子任务4.2: 测试存储隔离机制
  - [ ] 子任务4.3: 测试项目管理器功能

## Dev Notes

### 架构约束和模式

**混合数据管理策略** [Source: docs/architecture-decisions-2025-11-18.md#混合数据管理]
- 使用SQLite存储结构化项目配置数据
- 使用文件系统存储大容量内容（章节、角色详情等）
- 确保项目间数据完全隔离

**分层架构约束** [Source: docs/architecture-decisions-2025-11-18.md#分层组件架构]
- 数据访问层：database_manager.py, file_storage_manager.py
- 服务层：新增project_service.py
- 业务层：增强project_manager.py

**关键组件职责**
- `Project`模型：定义项目数据结构和属性
- `HybridDataManager`：处理混合存储逻辑和项目隔离
- `ProjectManager`：项目管理业务逻辑和生命周期

### 项目结构对齐

**目标文件结构** [Source: docs/architecture-decisions-2025-11-18.md#目录结构设计]
```
InfiniteQuill/
├── project_manager.py         # 增强支持多项目
├── models/
│   └── project_model.py       # 新建：项目数据模型
├── services/
│   └── project_service.py     # 新建：项目业务服务
├── data/
│   ├── database_manager.py    # 扩展：项目隔离支持
│   ├── file_storage_manager.py # 扩展：项目路径管理
│   └── hybrid_data_manager.py # 扩展：多项目混合存储
└── projects/                  # 新建：项目数据目录
    ├── {project_id}/
    │   ├── config/
    │   ├── characters/
    │   ├── content/
    │   └── exports/
```

**命名模式约定** [Source: docs/architecture-decisions-2025-11-18.md#命名模式]
- 项目ID格式：`proj_{timestamp}_{uuid_short}`
- 项目配置文件：`project_config.json`
- 数据库命名：`projects_{project_id}.db`
- 文件存储路径：`projects/{project_id}/{type}/`

### 技术实现要点

**项目ID生成机制**
- 结合时间戳和UUID确保唯一性
- 格式：`proj_20251118_abc123`
- 避免文件系统路径冲突

**数据隔离策略**
- 每个项目独立的SQLite数据库
- 文件系统使用项目子目录隔离
- 配置文件按项目分别存储

**默认项目模板**
- 预定义基础配置结构
- 标准化目录布局
- 初始化示例数据

### 测试策略

**单元测试覆盖**
- Project模型类所有属性和方法
- 数据隔离机制的边界测试
- 项目ID唯一性生成测试
- 默认配置模板验证

**集成测试重点**
- 多项目并发创建和访问
- 数据持久化和恢复
- 项目间数据泄漏检测

### 性能考虑

**初始化性能**
- 延迟加载非关键数据
- 异步初始化可选组件
- 缓存项目配置信息

**存储优化**
- 定期清理临时文件
- 压缩历史数据
- 监控存储空间使用

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

### Completion Notes List

### File List

## 变更日志

- **2025-11-18**: Story初始创建，基于Epic 1.1需求和架构决策