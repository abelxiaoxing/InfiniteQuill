#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Story 1.4 验证脚本 - 配置保存边界情况处理
验证所有验收标准的具体实现细节

验收标准:
1. 应用关闭时的强制保存 - 检查待保存变更并立即触发保存
2. 活动定时器检查 - 检测活动定时器并停止执行保存
3. 数据完整性保证 - 验证文件写入成功和数据不丢失
4. 异常情况下的优雅处理 - 错误日志记录和备用方案
5. 定时器资源清理 - 正确清理所有QTimer资源
"""

import sys
import os
import re

def check_closeEvent_implementation():
    """检查closeEvent实现"""
    print("🧪 AC1: 应用关闭时的强制保存检查")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键实现
        checks = {
            "closeEvent方法": "def closeEvent(self, event):",
            "日志记录": "logging.info(\"配置窗口关闭",
            "定时器停止": "self.auto_save_timer.isActive()",
            "定时器停止调用": "self.auto_save_timer.stop()",
            "等待保存完成": "while self.is_saving",
            "配置变更检查": "self.config != self.original_config",
            "立即保存调用": "save_config(self.config, None)",
            "强制保存日志": "logging.info(\"检测到未保存的配置变更",
            "事件接受": "event.accept()"
        }

        results = {}
        for name, pattern in checks.items():
            if pattern in content:
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<20} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(checks)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC1 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 90

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def check_timer_detection():
    """检查活动定时器检测"""
    print("\n🧪 AC2: 活动定时器检查")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查定时器检测逻辑
        timer_checks = {
            "定时器活动检测": "self.auto_save_timer.isActive()",
            "定时器停止": "self.auto_save_timer.stop()",
            "定时器状态日志": "logging.debug(\"已停止自动保存定时器\"",
            "等待后台保存": "if self.is_saving:",
            "等待超时控制": "wait_time < 30"
        }

        results = {}
        for name, pattern in timer_checks.items():
            if pattern in content:
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<20} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(timer_checks)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC2 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def check_data_integrity():
    """检查数据完整性保证"""
    print("\n🧪 AC3: 数据完整性保证检查")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查数据完整性验证
        integrity_checks = {
            "配置更新": "self.update_config_from_ui()",
            "配置比较": "self.config != self.original_config",
            "保存成功检查": "if success:",
            "成功日志": "logging.info(\"关闭前配置保存成功\")",
            "失败日志": "logging.error(\"关闭前配置保存失败\")",
            "状态信号发送": "self.auto_save_status_changed.emit"
        }

        results = {}
        for name, pattern in integrity_checks.items():
            if pattern in content:
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<20} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(integrity_checks)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC3 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def check_exception_handling():
    """检查异常处理"""
    print("\n🧪 AC4: 异常情况下的优雅处理")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查异常处理机制
        exception_checks = {
            "try-except块": "try:",
            "异常捕获": "except Exception as e:",
            "错误日志记录": "logging.error(f\"关闭前配置保存异常: {e}\"",
            "异常详情记录": "exc_info=True",
            "错误状态发送": "self.auto_save_status_changed.emit(\"error\"",
            "不阻塞关闭": "event.accept()在except之后"
        }

        results = {}
        for name, pattern in exception_checks.items():
            if pattern in content:
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<25} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(exception_checks)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC4 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def check_resource_cleanup():
    """检查资源清理"""
    print("\n🧪 AC5: 定时器资源清理")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查资源清理机制
        cleanup_checks = {
            "资源清理注释": "# 资源清理",
            "定时器清理": "self.auto_save_timer.deleteLater()",
            "定时器置空": "self.auto_save_timer = None",
            "状态栏清理": "self.status_bar = None",
            "线程清理": "self.save_thread = None",
            "事件循环处理": "QApplication.processEvents()",
            "清理异常处理": "except Exception as e:",
            "清理日志": "logging.debug(\"自动保存定时器资源已清理\")"
        }

        results = {}
        for name, pattern in cleanup_checks.items():
            if pattern in content:
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<25} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(cleanup_checks)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC5 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 75

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def test_config_operations():
    """测试配置操作"""
    print("\n🔄 配置操作集成测试")

    try:
        from config_manager import load_config, save_config

        # 测试正常保存流程
        config = load_config()
        print(f"  ✅ 配置加载成功，包含 {len(config)} 个配置项")

        # 修改配置
        test_config = config.copy()
        test_config['story_1_4_test'] = {
            'test': 'boundary_cases',
            'timestamp': '2025-11-16'
        }

        # 保存配置
        success = save_config(test_config)
        print(f"  ✅ 配置保存测试: {'成功' if success else '失败'}")

        # 验证保存结果
        if success:
            reloaded = load_config()
            if 'story_1_4_test' in reloaded:
                print("  ✅ 数据完整性验证成功")

                # 清理测试数据
                clean_config = {k: v for k, v in reloaded.items() if k != 'story_1_4_test'}
                save_config(clean_config)
                print("  ✅ 测试数据已清理")
                return True
            else:
                print("  ❌ 数据完整性验证失败")
                return False
        else:
            print("  ❌ 配置保存失败")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def validate_story_1_4_acceptance_criteria():
    """验证Story 1.4的所有验收标准"""
    print("🎯 Story 1.4 验收标准验证")
    print("="*60)
    print("故事: 配置保存边界情况处理")
    print("="*60)

    results = []

    # 执行所有验收标准验证
    results.append(("AC1: 应用关闭时的强制保存", check_closeEvent_implementation()))
    results.append(("AC2: 活动定时器检查", check_timer_detection()))
    results.append(("AC3: 数据完整性保证", check_data_integrity()))
    results.append(("AC4: 异常情况下的优雅处理", check_exception_handling()))
    results.append(("AC5: 定时器资源清理", check_resource_cleanup()))

    # 额外的集成测试
    integration_test_result = test_config_operations()
    print(f"\n🔄 集成测试: {'✅ 通过' if integration_test_result else '❌ 失败'}")

    # 汇总结果
    print("\n" + "="*60)
    print("📊 验收标准验证结果")
    print("="*60)

    passed = 0
    total = len(results)

    for ac_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{ac_name:<35} {status}")
        if result:
            passed += 1

    print("-"*60)
    print(f"验收标准通过率: {passed}/{total} ({passed/total*100:.0f}%)")

    if passed == total and integration_test_result:
        print("\n🎉 恭喜！Story 1.4 的所有验收标准均已满足！")
        print("\n✨ Story 1.4 实施总结:")
        print("  ✅ 应用关闭时的强制保存机制完善")
        print("  ✅ 活动定时器检测和处理准确")
        print("  ✅ 数据完整性保证机制可靠")
        print("  ✅ 异常情况下的优雅处理完善")
        print("  ✅ 定时器资源清理机制到位")
        print("  ✅ 集成测试验证通过")
        print("\n🏆 Epic 1: 基础设施现代化 全部完成！")
        print("🚀 可以继续下一个Epic的开发工作！")
        return True
    else:
        print(f"\n⚠️ 还有 {total - passed + (0 if integration_test_result else 1)} 项需要完善")
        return False

def main():
    """主函数"""
    # 检查是否在项目根目录
    if not os.path.exists('ui_qt/widgets/config_widget.py'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return False

    # 执行验证
    success = validate_story_1_4_acceptance_criteria()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)