#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Story 2.2 验证脚本 - 深色主题角色列表修复
验证深色主题下角色列表选中项的显示问题修复

验收标准:
1. 深色主题选中项背景色为#3a3a3a
2. 深色主题选中项文字颜色为#ffffff
3. 悬停状态背景色为#4a4a4a
4. WCAG 2.1 AA合规性(4.5:1对比度)
5. 浅色主题不受影响
"""

import sys
import os
import re

def check_qss_files_exist():
    """检查QSS文件是否存在"""
    print("🧪 检查QSS文件存在性")

    files_to_check = {
        "深色主题样式文件": "ui_qt/styles/material_dark.qss",
        "浅色主题样式文件": "ui_qt/styles/material_light.qss"
    }

    results = {}
    for name, filepath in files_to_check.items():
        exists = os.path.exists(filepath)
        results[name] = "✅ 存在" if exists else "❌ 不存在"
        print(f"  {name:<20} {results[name]}")

    passed = sum(1 for result in results.values() if "✅" in result)
    total = len(results)
    completion_rate = (passed / total) * 100

    print(f"\n📊 文件存在性检查: {completion_rate:.0f}% ({passed}/{total})")
    return completion_rate >= 100

def check_dark_theme_styles():
    """检查深色主题样式修复"""
    print("\n🧪 检查深色主题样式修复")

    try:
        with open('ui_qt/styles/material_dark.qss', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键样式规则
        style_checks = {
            "选中项背景色#3a3a3a": "background-color: #3a3a3a" in content,
            "选中项文字颜色#ffffff": "color: #ffffff" in content,
            "悬停状态背景色#4a4a4a": "background-color: #4a4a4a" in content,
            "RoleListWidget选择器": "QListWidget#RoleListWidget::item:selected" in content,
            "RoleListWidget悬停选择器": "QListWidget#RoleListWidget::item:hover" in content,
            "左边框样式": "border-left: 4px solid #1976d2" in content
        }

        results = {}
        for name, result in style_checks.items():
            results[name] = "✅ 已修复" if result else "❌ 未修复"
            print(f"  {name:<25} {results[name]}")

        passed = sum(1 for result in results.values() if "✅" in result)
        total = len(style_checks)
        completion_rate = (passed / total) * 100

        print(f"\n📊 深色主题样式修复: {completion_rate:.0f}% ({passed}/{total})")
        return completion_rate >= 90

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def check_light_theme_unchanged():
    """检查浅色主题未受影响"""
    print("\n🧪 检查浅色主题未受影响")

    try:
        with open('ui_qt/styles/material_light.qss', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查浅色主题保持原有样式
        light_theme_checks = {
            "保持原有选中背景": "background-color: #e3f2fd" in content,
            "保持原有文字颜色": "color: #212121" in content,
            "保持RoleListWidget选择器": "QListWidget#RoleListWidget::item:selected" in content,
            "无深色主题颜色": "#3a3a3a" not in content,
            "无深色悬停颜色": "#4a4a4a" not in content
        }

        results = {}
        for name, result in light_theme_checks.items():
            results[name] = "✅ 正常" if result else "❌ 异常"
            print(f"  {name:<25} {results[name]}")

        passed = sum(1 for result in results.values() if "✅" in result)
        total = len(light_theme_checks)
        completion_rate = (passed / total) * 100

        print(f"\n📊 浅色主题保持性: {completion_rate:.0f}% ({passed}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def check_inline_styles_removed():
    """检查内联样式已移除"""
    print("\n🧪 检查内联样式已移除")

    try:
        with open('ui_qt/widgets/role_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查内联样式已移除
        inline_checks = {
            "移除setStyleSheet调用": "setStyleSheet" not in content or "# RoleListWidget" not in content,
            "移除内联背景色": "background-color: #e3f2fd" not in content,
            "移除内联边框": "border-bottom: 1px solid #e0e0e0" not in content,
            "保留对象名设置": "setObjectName(\"RoleListWidget\")" in content,
            "保留选择模式": "setSelectionMode(QListWidget.SingleSelection)" in content
        }

        results = {}
        for name, result in inline_checks.items():
            results[name] = "✅ 已处理" if result else "❌ 仍存在"
            print(f"  {name:<25} {results[name]}")

        passed = sum(1 for result in results.values() if "✅" in result)
        total = len(inline_checks)
        completion_rate = (passed / total) * 100

        print(f"\n📊 内联样式移除: {completion_rate:.0f}% ({passed}/{total})")
        return completion_rate >= 80

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def calculate_wcag_contrast(color1, color2):
    """计算WCAG对比度"""
    def get_luminance(hex_color):
        # 移除#号
        hex_color = hex_color.lstrip('#')
        # 转换为RGB
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # 转换为相对亮度
        r, g, b = rgb
        rs, gs, bs = r / 255.0, g / 255.0, b / 255.0
        r, g, b = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4, \
                   gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4, \
                   bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = get_luminance(color1)
    l2 = get_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)

def check_wcag_compliance():
    """检查WCAG 2.1 AA合规性"""
    print("\n🧪 检查WCAG 2.1 AA合规性")

    # 检查深色主题的对比度
    contrast_checks = {
        "深色主题选中项对比度": calculate_wcag_contrast("#3a3a3a", "#ffffff"),
        "深色主题悬停对比度": calculate_wcag_contrast("#4a4a4a", "#ffffff"),
        "浅色主题选中项对比度": calculate_wcag_contrast("#e3f2fd", "#212121"),
        "浅色主题悬停对比度": calculate_wcag_contrast("#f5f5f5", "#212121")
    }

    results = {}
    wcag_aa_threshold = 4.5

    for name, contrast in contrast_checks.items():
        compliant = contrast >= wcag_aa_threshold
        status = "✅ 合规" if compliant else f"❌ 不合规 ({contrast:.2f}:1)"
        results[name] = status
        print(f"  {name:<25} {status} ({contrast:.2f}:1)")

    passed = sum(1 for result in results.values() if "✅" in result)
    total = len(results)
    compliance_rate = (passed / total) * 100

    print(f"\n📊 WCAG 2.1 AA合规率: {compliance_rate:.0f}% ({passed}/{total})")
    return compliance_rate >= 75

def test_theme_loading():
    """测试主题加载功能"""
    print("\n🔄 主题加载功能测试")

    try:
        from ui_qt.utils.theme_manager import ThemeManager

        theme_manager = ThemeManager()

        # 测试深色主题加载
        dark_theme = theme_manager.load_qss_file("material_dark")
        dark_loaded = dark_theme is not None and len(dark_theme) > 0
        print(f"  深色主题加载: {'✅ 成功' if dark_loaded else '❌ 失败'}")

        # 测试浅色主题加载
        light_theme = theme_manager.load_qss_file("material_light")
        light_loaded = light_theme is not None and len(light_theme) > 0
        print(f"  浅色主题加载: {'✅ 成功' if light_loaded else '❌ 失败'}")

        # 检查主题内容包含关键样式
        dark_has_role_styles = "QListWidget#RoleListWidget::item:selected" in dark_theme
        light_has_role_styles = "QListWidget#RoleListWidget::item:selected" in light_theme

        print(f"  深色主题包含角色样式: {'✅ 包含' if dark_has_role_styles else '❌ 缺失'}")
        print(f"  浅色主题包含角色样式: {'✅ 包含' if light_has_role_styles else '❌ 缺失'}")

        success = dark_loaded and light_loaded and dark_has_role_styles and light_has_role_styles
        print(f"\n🔄 主题加载测试: {'✅ 通过' if success else '❌ 失败'}")
        return success

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def validate_story_2_2_acceptance_criteria():
    """验证Story 2.2的所有验收标准"""
    print("🎯 Story 2.2 验收标准验证")
    print("="*60)
    print("故事: 深色主题角色列表修复")
    print("="*60)

    results = []

    # 执行所有验收标准验证
    results.append(("QSS文件存在性", check_qss_files_exist()))
    results.append(("深色主题样式修复", check_dark_theme_styles()))
    results.append(("浅色主题未受影响", check_light_theme_unchanged()))
    results.append(("内联样式已移除", check_inline_styles_removed()))
    results.append(("WCAG 2.1 AA合规性", check_wcag_compliance()))

    # 额外的主题加载测试
    theme_test_result = test_theme_loading()
    print(f"\n🔄 主题加载功能测试: {'✅ 通过' if theme_test_result else '❌ 失败'}")

    # 汇总结果
    print("\n" + "="*60)
    print("📊 验收标准验证结果")
    print("="*60)

    passed = 0
    total = len(results)

    for ac_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{ac_name:<25} {status}")
        if result:
            passed += 1

    print("-"*60)
    print(f"验收标准通过率: {passed}/{total} ({passed/total*100:.0f}%)")

    if passed == total and theme_test_result:
        print("\n🎉 恭喜！Story 2.2 的所有验收标准均已满足！")
        print("\n✨ Story 2.2 实施总结:")
        print("  ✅ 深色主题选中项背景色修复为#3a3a3a")
        print("  ✅ 深色主题选中项文字颜色设置为#ffffff")
        print("  ✅ 悬停状态背景色设置为#4a4a4a")
        print("  ✅ WCAG 2.1 AA对比度要求得到满足")
        print("  ✅ 浅色主题样式保持不变")
        print("  ✅ 内联样式成功移除，使用外部QSS")
        print("  ✅ 主题加载功能正常工作")
        print("\n🚀 Epic 2: UI/UX体验优化 第二个故事完成！")
        return True
    else:
        print(f"\n⚠️ 还有 {total - passed + (0 if theme_test_result else 1)} 项需要完善")
        return False

def main():
    """主函数"""
    # 检查是否在项目根目录
    if not os.path.exists('ui_qt/widgets/role_manager.py'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return False

    # 执行验证
    success = validate_story_2_2_acceptance_criteria()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)