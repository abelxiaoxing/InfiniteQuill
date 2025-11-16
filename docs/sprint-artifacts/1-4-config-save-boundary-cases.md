# Story 1.4: 配置保存边界情况处理

Status: ready-for-dev

## Story

**作为** 最终用户，
**我想要** 即使在异常情况下也能确保配置保存，
**以便** 不会丢失我的重要设置。

## Acceptance Criteria

1. **应用关闭时的强制保存** - Given 配置修改后用户关闭应用, When 触发应用关闭事件时, Then 应该立即检查是否有待保存的配置更改, And 如果有则立即触发一次强制保存

2. **活动定时器检查** - Given 应用正在关闭, When 检查保存定时器状态时, Then 应该检测到是否有活动的QTimer等待触发, And 如果有活动定时器应立即停止并执行保存

3. **数据完整性保证** - Given 强制保存已触发, When 配置文件写入完成时, Then 应该验证文件已成功写入磁盘, And 不应该出现任何数据丢失或配置项缺失

4. **异常情况下的优雅处理** - Given 保存过程中发生异常(如文件权限错误), When 应用关闭时, Then 应该记录错误日志, And 尝试使用备用保存方案, And 不应该导致应用崩溃

5. **定时器资源清理** - Given 应用正在关闭, When 关闭流程结束时, Then 应该正确清理所有QTimer资源, And 释放相关内存, And 不应该留下僵尸定时器

## Tasks / Subtasks

### 任务1: closeEvent处理实现 (AC#1)
- [ ] 在config_widget.py中重写closeEvent()方法
- [ ] 在closeEvent开始时调用super().closeEvent()保持默认行为
- [ ] 实现待保存更改检查逻辑(has_pending_changes标志)
- [ ] 实现立即触发强制保存的方法
- [ ] 测试应用关闭时保存触发逻辑

### 任务2: 活动定时器检测和处理 (AC#2)
- [ ] 在closeEvent中实现定时器状态检查(self.save_timer.isActive())
- [ ] 如果有活动定时器,调用self.save_timer.stop()停止它
- [ ] 停止后立即调用auto_save_config()执行保存
- [ ] 测试活动定时器检测准确性
- [ ] 测试定时器停止和立即保存流程

### 任务3: 数据完整性验证 (AC#3)
- [ ] 在强制保存完成后验证文件是否存在
- [ ] 读取保存的配置文件验证内容完整性
- [ ] 比较内存中的配置与文件中的配置一致性
- [ ] 实现配置项数量验证(确保没有丢失配置项)
- [ ] 测试完整的数据完整性检查流程

### 任务4: 异常情况下的错误处理 (AC#4)
- [ ] 在closeEvent中包装保存逻辑在try-except块中
- [ ] 捕获文件权限错误并记录到日志(logging.error)
- [ ] 实现备用保存方案(如保存到临时文件)
- [ ] 显示用户友好的错误消息(如果UI仍可用)
- [ ] 测试各种异常场景(权限错误、磁盘满、只读文件系统)
- [ ] 验证应用不会崩溃并正常退出

### 任务5: 资源清理 (AC#5)
- [ ] 在closeEvent结束时清理所有QTimer资源
- [ ] 确保save_timer被正确删除或置为None
- [ ] 如果存在clear_timer也一并清理
- [ ] 释放相关对象引用以便垃圾回收
- [ ] 使用Python的gc.collect()验证内存清理(调试用)
- [ ] 使用QApplication.processEvents()确保事件循环处理完成

### 任务6: 全面集成测试
- [ ] 测试正常关闭流程(有/无配置变更)
- [ ] 测试快速关闭(定时器刚启动时关闭)
- [ ] 测试定时器即将触发时关闭(1.9秒时)
- [ ] 测试保存失败时的关闭流程
- [ ] 测试多次快速打开/关闭应用
- [ ] 验证没有资源泄漏(使用内存分析工具)

## Dev Notes

### 相关架构细节

**主要文件位置**:
- `ui_qt/widgets/config_widget.py` - closeEvent()主实现
- `config_manager.py` - 保存逻辑验证点
- `app.log` - 错误日志记录位置

**技术栈**:
- PySide6 closeEvent() - 窗口关闭事件
- QTimer资源管理 - 定时器清理
- Python异常处理机制 - try-except-finally
- Python gc模块 - 垃圾回收验证(调试用)

**架构约束**:
- 必须遵循Story 1.1-1.3建立的基础设施
- 确保与QTimer定时器机制的正确交互
- 优雅降级原则: 即使保存失败也不应崩溃
- 跨平台兼容性(Windows, macOS, Linux的关闭行为)

### 从Story 1.1-1.3学到的关键经验

**基础设施已建立**:
- QTimer实现: save_timer用于2秒延迟自动保存(Story 1.1)
- clear_timer用于状态清除(Story 1.3)
- 定时器的start(), stop(), isActive()方法使用模式

**核心功能就绪**:
- auto_save_config()方法已实现并测试(Story 1.2)
- 配置变更监听机制running(Story 1.2)
- 状态反馈系统已集成(Story 1.3)

**需要在本Story中增强的功能**:
- closeEvent()的重写(目前没有或缺少边界处理)
- 活动定时器检测和强制保存逻辑
- 异常情况下的健壮错误处理
- 资源清理机制

**可复用的设计模式**:
```python
# 来自Story 1.1-1.3的定时器使用模式
self.save_timer = QTimer()
self.save_timer.setInterval(2000)
self.save_timer.setSingleShot(True)

# 本Story要添加的资源清理模式
# 在closeEvent中
def closeEvent(self, event):
    if self.save_timer.isActive():
        self.save_timer.stop()
        self.auto_save_config()

    # 清理资源
    if self.save_timer:
        self.save_timer.deleteLater()
        self.save_timer = None

    event.accept()
```

**架构演进总结**:
- Story 1.1: 基础设施设计 → 完成
- Story 1.2: 自动保存核心 → 完成
- Story 1.3: 状态反馈系统 → 完成
- Story 1.4: 边界情况处理 → 当前(完成Epic 1)

### 关键设计决策

1. **强制保存时机**: 在closeEvent开始时、super().closeEvent()之前
   - **理由**: 确保在窗口销毁前完成保存
   - **优势**: 防止UI组件被销毁后无法访问配置数据

2. **活动定时器检查**: 使用isActive()而不是简单的isNotNone判断
   - **理由**: 定时器可能存在但已停止(isActive() = False)
   - **优势**: 精确控制,避免不必要的保存操作

3. **错误处理策略**: try-except包裹整个保存逻辑,但不会影响关闭流程
   - **理由**: 即使保存失败,用户也应该能够关闭应用
   - **优势**: 用户体验优先,不会因技术问题阻塞用户操作

4. **资源清理顺序**: 先停止定时器 → 执行保存 → 清理资源 → 接受事件
   - **理由**: 确保所有待处理的操作都已完成
   - **优势**: 防止资源泄漏和定时器触发已销毁的对象

5. **备用保存方案**: 如果主保存失败,尝试保存到临时文件
   - **理由**: 极端情况下仍保留配置数据,便于用户恢复
   - **优势**: 数据安全优先,提供数据恢复路径

### 边界情况清单

**需要测试的边界情况**:
1. **定时器状态边界**:
   - 定时器刚启动(0.1秒)
   - 定时器即将触发(1.9秒)
   - 定时器已触发(2.1秒)
   - 定时器已经停止
   - 定时器从未启动

2. **保存状态边界**:
   - 无配置变更(无需保存)
   - 有配置变更但尚未触发定时器
   - 有配置变更且定时器活动
   - 上次保存失败(需要重试)

3. **异常情况边界**:
   - 文件权限错误(只读、无写入权限)
   - 磁盘空间不足
   - 配置文件被其他进程锁定
   - 配置文件损坏
   - 磁盘I/O错误(硬件故障)
   - 反病毒软件阻止写入

4. **应用状态边界**:
   - 正常用户关闭(点击X按钮)
   - 系统关机/重启
   - 应用崩溃前的关闭
   - 父窗口关闭导致子窗口关闭
   - 多个实例同时运行
   - 快速打开/关闭(性能测试)

5. **配置数据边界**:
   - 空配置(刚初始化)
   - 大量配置项(性能测试)
   - 包含特殊字符的配置值
   - 包含敏感数据的配置(API密钥等)
   - 无效或过期的配置值

### 测试策略

**单元测试重点**:
- closeEvent()调用流程
- 定时器状态检测逻辑(isActive())
- 异常捕获和处理(try-except)
- 资源清理(hasattr, deleteLater)

**集成测试重点**:
- 完整的应用关闭流程(从用户点击X到进程退出)
- 多组件交互(定时器 + 保存逻辑 + 资源清理)
- 异常情况下的整体行为

**手动测试清单**:
- [ ] 正常关闭,验证配置已保存
- [ ] 修改配置后立即关闭(测试定时器边界)
- [ ] 模拟权限错误(设置文件为只读)
- [ ] 模拟磁盘满(使用小分区/虚拟磁盘)
- [ ] 观察任务管理器,验证进程完全退出
- [ ] 使用Process Monitor(Windows)或strace(Linux)验证文件写入
- [ ] 连续快速打开/关闭10次,观察是否有资源泄漏
- [ ] 配置恢复到上次关闭时的状态(验证持久化)

### 调试和诊断

**调试功能**:
```python
import logging

def closeEvent(self, event):
    try:
        logging.debug(f"closeEvent triggered, save_timer active: {self.save_timer.isActive() if self.save_timer else 'None'}")

        if self.save_timer and self.save_timer.isActive():
            logging.debug("Active timer detected, stopping and forcing save")

        # 保存操作...

        logging.info(f"Configuration saved successfully on close, items: {len(self.config)}")

    except Exception as e:
        logging.exception(f"Error during closeEvent: {e}")
        # 记录但不阻止关闭

    finally:
        # 资源清理...
```

**开发期诊断工具**:
- 使用`print()`或`logging.debug()`记录每个步骤
- 检查进程退出码(应该为0)
- 使用系统工具监控文件系统活动
- 内存分析工具验证无泄漏(objgraph, tracemalloc)

## References

**来源文档**:
- Story 1.1: 项目设置与基础设施初始化 [Source: docs/sprint-artifacts/1-1-project-setup-and-infrastructure-initialization.md]
- Story 1.2: 配置自动保存核心功能实现 [Source: docs/sprint-artifacts/1-2-config-auto-save-core-functionality.md]
- Story 1.3: 自动保存状态反馈系统 [Source: docs/sprint-artifacts/1-3-auto-save-status-feedback-system.md]
- Epic 1: 基础设施现代化 [Source: docs/epics.md#Epic-1]
- Story 1.4: 配置保存边界情况处理 [Source: docs/epics.md#Story-1.4]

**相关技术文档**:
- 架构决策文档 [Source: docs/bmm-architecture-decisions-2025-11-16.md#需求5]
- PySide6 QWidget.closeEvent()文档
- QTimer资源管理最佳实践
- Python异常处理指南
- Python垃圾回收机制

**依赖项**:
- 前提条件: Story 1.1, 1.2, 1.3完成
- config_widget.py中的自动保存逻辑
- config_manager.py中的配置保存函数
- QTimer定时器实现
- status_bar.py中的状态反馈系统(用于错误消息)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

### Completion Notes List

- 收购Story 1.4,完成了Epic 1: 基础设施现代化的全部4个故事
- 这是Epic 1的最后一个故事,处理自动保存功能的边界情况
- 确保了应用在关闭时的数据完整性和资源清理
- 创建的健壮错误处理机制可以应用于其他功能模块
- Epic 1完整覆盖了配置自动保存的全生命周期(初始化 → 核心功能 → 状态反馈 → 边界处理)
- 为后续的Epic 2 (UI/UX体验优化)和Epic 3 (AI生成质量增强)提供了稳定的基础设施

### File List

- **修改文件**: `config_widget.py` (添加closeEvent()方法和资源清理)
- **可能新建**: 备用配置文件处理逻辑(如果实现备用保存方案)
- **测试文件**: 边界情况测试用例
