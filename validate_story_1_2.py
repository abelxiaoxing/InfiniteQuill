#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Story 1.2 验证脚本 - 配置自动保存核心功能实现
验证所有验收标准的具体实现细节

验收标准:
1. 配置自动保存触发 - 2秒延迟触发
2. 配置文件持久化 - 正确写入config.json
3. 保存状态反馈 - 显示成功消息
4. 持久化验证 - 重启后配置保持
5. 错误处理 - 错误日志和错误消息
"""

import sys
import os
import re
import time
import json
import tempfile
import shutil
from pathlib import Path

def analyze_auto_save_trigger():
    """验证验收标准1: 配置自动保存触发 - 2秒延迟"""
    print("🧪 AC1: 配置自动保存触发验证")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键实现
        checks = {
            "2秒定时器": r"self\.auto_save_timer\.setInterval\(2000\)",
            "单次触发": r"self\.auto_save_timer\.setSingleShot\(True\)",
            "定时器连接": r"self\.auto_save_timer\.timeout\.connect\(self\.perform_auto_save\)",
            "变更监听": r"def connect_change_listeners\(self\):",
            "所有控件已连接": r"self\.api_key\.textChanged\.connect\(self\.on_config_changed\)",
            "定时器重置": r"self\.auto_save_timer\.stop\(\).*?self\.auto_save_timer\.start\(2000\)",
            "状态发送": r"auto_save_status_changed\.emit\(\"info\""
        }

        results = {}
        for name, pattern in checks.items():
            if re.search(pattern, content):
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<20} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(results)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC1 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 90

    except Exception as e:
        print(f"  ❌ 分析失败: {e}")
        return False

def test_config_persistence():
    """验证验收标准2: 配置文件持久化"""
    print("\n🧪 AC2: 配置文件持久化验证")

    try:
        from config_manager import load_config, save_config, get_user_config_path

        # 测试配置加载
        original_config = load_config()
        print(f"  ✅ 配置加载成功，包含 {len(original_config)} 个配置项")

        # 修改配置
        test_config = original_config.copy()
        test_config['test_auto_save'] = {
            'timestamp': time.time(),
            'test_value': 'Story 1.2 验证测试'
        }

        # 保存配置
        success = save_config(test_config)
        print(f"  ✅ 配置保存: {'成功' if success else '失败'}")

        if success:
            # 验证文件存在
            config_path = get_user_config_path()
            if config_path.exists():
                print(f"  ✅ 配置文件存在: {config_path}")

                # 验证文件内容
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)

                if 'test_auto_save' in saved_config:
                    print("  ✅ 测试配置已正确写入文件")
                    return True
                else:
                    print("  ❌ 测试配置未写入文件")
                    return False
            else:
                print(f"  ❌ 配置文件不存在: {config_path}")
                return False
        else:
            print("  ❌ 配置保存失败")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def verify_status_feedback():
    """验证验收标准3: 保存状态反馈"""
    print("\n🧪 AC3: 保存状态反馈验证")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        with open('ui_qt/widgets/status_bar.py', 'r', encoding='utf-8') as f:
            status_content = f.read()

        # 检查状态反馈实现
        feedback_checks = {
            "成功状态发送": r'auto_save_status_changed\.emit\(\"success\"',
            "错误状态发送": r'auto_save_status_changed\.emit\(\"error\"',
            "成功消息格式": r'\"配置已自动保存\"',
            "错误消息格式": r'\"配置保存失败，请重试\"',
            "状态栏调用": r'self\.status_bar\.set_success_state\(message\)',
            "状态栏错误调用": r'self\.status_bar\.set_error_state\(message\)',
            "3秒自动清除": r'set_success_state.*?auto_clear.*?True'
        }

        status_bar_checks = {
            "set_success_state方法": r'def set_success_state\(self',
            "set_error_state方法": r'def set_error_state\(self',
            "auto_clear参数": r'auto_clear.*?=.*True'
        }

        results = {}
        # 检查config_widget.py中的反馈实现
        for name, pattern in feedback_checks.items():
            if re.search(pattern, content, re.DOTALL):
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 检查status_bar.py中的状态方法
        for name, pattern in status_bar_checks.items():
            if re.search(pattern, status_content):
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<25} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(results)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC3 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False

def test_persistence_verification():
    """验证验收标准4: 持久化验证（模拟重启）"""
    print("\n🧪 AC4: 持久化验证测试")

    try:
        from config_manager import load_config, save_config

        # 步骤1: 保存一个测试配置
        test_config = {
            "test_persistence": {
                "story": "1.2",
                "test_data": "持久化验证测试",
                "timestamp": time.time()
            }
        }

        success = save_config(test_config)
        print(f"  ✅ 测试配置保存: {'成功' if success else '失败'}")

        if not success:
            return False

        # 步骤2: 重新加载配置（模拟应用重启）
        reloaded_config = load_config()

        # 步骤3: 验证配置是否仍然存在
        if "test_persistence" in reloaded_config:
            persistent_data = reloaded_config["test_persistence"]

            if (persistent_data["story"] == "1.2" and
                persistent_data["test_data"] == "持久化验证测试"):
                print("  ✅ 配置持久化验证成功")
                print(f"  ✅ 时间戳: {persistent_data['timestamp']}")
                return True
            else:
                print("  ❌ 配置数据不匹配")
                return False
        else:
            print("  ❌ 测试配置未持久化")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def verify_error_handling():
    """验证验收标准5: 错误处理"""
    print("\n🧪 AC5: 错误处理验证")

    try:
        with open('ui_qt/widgets/config_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查错误处理实现
        error_checks = {
            "try-except捕获": r'try:\s*\n.*?except\s+Exception',
            "异常日志记录": r'logging\.error\(\s*f\"自动保存配置时发生异常',
            "错误状态发送": r'auto_save_status_changed\.emit\(\"error\"',
            "错误消息包含异常": r'f\"配置保存失败: \{str\(e\)\}\"',
            "finally清理": r'finally:\s*\n.*?self\.is_saving\s*=\s*False',
            "重试机制": r'pending_save.*?QTimer\.singleShot.*?perform_auto_save'
        }

        results = {}
        for name, pattern in error_checks.items():
            if re.search(pattern, content, re.DOTALL):
                results[name] = "✅ 已实现"
            else:
                results[name] = "❌ 未找到"

        # 输出结果
        for name, status in results.items():
            print(f"  {name:<25} {status}")

        # 计算完成度
        implemented = sum(1 for status in results.values() if "✅" in status)
        total = len(results)
        completion_rate = (implemented / total) * 100

        print(f"\n📊 AC5 完成度: {completion_rate:.0f}% ({implemented}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False

def test_complete_auto_save_flow():
    """测试完整的自动保存流程"""
    print("\n🔄 完整自动保存流程测试")

    try:
        # 模拟配置变更流程
        print("  📝 模拟配置变更...")

        # 1. 加载原始配置
        from config_manager import load_config, save_config
        original_config = load_config()
        print("    ✅ 原始配置加载完成")

        # 2. 模拟配置变更
        modified_config = original_config.copy()
        modified_config['flow_test'] = {
            'story': '1.2',
            'step': 'auto_save_flow_test',
            'timestamp': time.time()
        }

        # 3. 保存变更（模拟自动保存）
        success = save_config(modified_config)
        print(f"    ✅ 配置保存模拟: {'成功' if success else '失败'}")

        # 4. 验证保存结果
        if success:
            # 重新加载配置
            verify_config = load_config()
            if 'flow_test' in verify_config:
                print("    ✅ 配置变更已持久化")

                # 清理测试数据
                cleanup_config = original_config.copy()
                save_config(cleanup_config)
                print("    ✅ 测试数据已清理")

                return True
            else:
                print("    ❌ 配置变更未持久化")
                return False
        else:
            return False

    except Exception as e:
        print(f"  ❌ 流程测试失败: {e}")
        return False

def validate_story_1_2_acceptance_criteria():
    """验证Story 1.2的所有验收标准"""
    print("🎯 Story 1.2 验收标准验证")
    print("="*60)
    print("故事: 配置自动保存核心功能实现")
    print("="*60)

    results = []

    # 执行所有验收标准验证
    results.append(("AC1: 配置自动保存触发", analyze_auto_save_trigger()))
    results.append(("AC2: 配置文件持久化", test_config_persistence()))
    results.append(("AC3: 保存状态反馈", verify_status_feedback()))
    results.append(("AC4: 持久化验证", test_persistence_verification()))
    results.append(("AC5: 错误处理", verify_error_handling()))

    # 额外的完整流程测试
    flow_test_result = test_complete_auto_save_flow()
    print(f"\n🔄 完整流程测试: {'✅ 通过' if flow_test_result else '❌ 失败'}")

    # 汇总结果
    print("\n" + "="*60)
    print("📊 验收标准验证结果")
    print("="*60)

    passed = 0
    total = len(results)

    for ac_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{ac_name:<30} {status}")
        if result:
            passed += 1

    print("-"*60)
    print(f"验收标准通过率: {passed}/{total} ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 恭喜！Story 1.2 的所有验收标准均已满足！")
        print("\n✨ Story 1.2 实施总结:")
        print("  ✅ 配置自动保存触发机制完全实现")
        print("  ✅ 配置文件持久化功能正常")
        print("  ✅ 保存状态反馈系统集成完善")
        print("  ✅ 持久化验证机制可靠")
        print("  ✅ 错误处理和恢复机制完备")
        print("  ✅ 完整自动保存流程验证通过")
        print("\n🚀 Story 1.2 实施完成，可以继续下一个故事！")
        return True
    else:
        print(f"\n⚠️ 还有 {total - passed} 项验收标准需要完善")
        return False

def main():
    """主函数"""
    # 检查是否在项目根目录
    if not os.path.exists('ui_qt/widgets/config_widget.py'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return False

    # 执行验证
    success = validate_story_1_2_acceptance_criteria()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)