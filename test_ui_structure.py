#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI结构测试脚本
验证PySide6界面模块的导入和结构完整性
"""

import os
import sys
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")

    try:
        # 测试PySide6
        from PySide6.QtWidgets import QApplication, QMainWindow
        from PySide6.QtCore import Qt, Signal
        from PySide6.QtGui import QIcon
        print("  ✅ PySide6核心模块导入成功")
    except ImportError as e:
        print(f"  ❌ PySide6导入失败: {e}")
        return False

    # 测试自定义模块
    try:
        # 测试工具模块
        from ui_qt.utils.theme_manager import ThemeManager
        from ui_qt.utils.ui_helpers import create_separator
        print("  ✅ UI工具模块导入成功")
    except ImportError as e:
        print(f"  ❌ UI工具模块导入失败: {e}")
        return False

    try:
        # 测试组件模块
        from ui_qt.widgets.status_bar import StatusBar
        from ui_qt.widgets.config_widget import ConfigWidget
        print("  ✅ UI组件模块导入成功")
    except ImportError as e:
        print(f"  ❌ UI组件模块导入失败: {e}")
        return False

    try:
        # 测试对话框模块
        from ui_qt.dialogs.settings_dialog import SettingsDialog
        from ui_qt.dialogs.progress_dialog import ProgressDialog
        print("  ✅ 对话框模块导入成功")
    except ImportError as e:
        print(f"  ❌ 对话框模块导入失败: {e}")
        return False

    return True

def test_file_structure():
    """测试文件结构"""
    print("\n📁 检查文件结构...")

    required_files = [
        "ui_qt/__init__.py",
        "ui_qt/main_window.py",
        "ui_qt/utils/__init__.py",
        "ui_qt/utils/theme_manager.py",
        "ui_qt/utils/ui_helpers.py",
        "ui_qt/widgets/__init__.py",
        "ui_qt/widgets/status_bar.py",
        "ui_qt/widgets/config_widget.py",
        "ui_qt/widgets/generation_widget.py",
        "ui_qt/widgets/chapter_editor.py",
        "ui_qt/widgets/role_manager.py",
        "ui_qt/dialogs/__init__.py",
        "ui_qt/dialogs/settings_dialog.py",
        "ui_qt/dialogs/progress_dialog.py",
        "ui_qt/dialogs/role_import_dialog.py",
        "ui_qt/styles/__init__.py",
        "main_qt.py",
        "start_qt_ui.py"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")

    if missing_files:
        print(f"\n  ❌ 缺少文件:")
        for file_path in missing_files:
            print(f"     - {file_path}")
        return False

    return True

def test_ui_components():
    """测试UI组件实例化"""
    print("\n🧪 测试UI组件...")

    # 创建临时应用实例
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # 测试主题管理器
        from ui_qt.utils.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        print("  ✅ 主题管理器创建成功")

        # 测试状态栏
        from ui_qt.widgets.status_bar import StatusBar
        status_bar = StatusBar()
        print("  ✅ 状态栏创建成功")

        # 测试配置组件（需要配置）
        from ui_qt.widgets.config_widget import ConfigWidget
        config_widget = ConfigWidget({})
        print("  ✅ 配置组件创建成功")

        return True

    except Exception as e:
        print(f"  ❌ 组件测试失败: {e}")
        return False

def test_theme_manager():
    """测试主题管理器"""
    print("\n🎨 测试主题管理器...")

    try:
        from ui_qt.utils.theme_manager import ThemeManager
        theme_manager = ThemeManager()

        # 测试浅色主题
        light_css = theme_manager.get_light_theme()
        if light_css and len(light_css) > 100:
            print("  ✅ 浅色主题样式生成成功")
        else:
            print("  ❌ 浅色主题样式生成失败")
            return False

        # 测试深色主题
        dark_css = theme_manager.get_dark_theme()
        if dark_css and len(dark_css) > 100:
            print("  ✅ 深色主题样式生成成功")
        else:
            print("  ❌ 深色主题样式生成失败")
            return False

        return True

    except Exception as e:
        print(f"  ❌ 主题管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║             UI结构完整性测试 - PySide6版本                  ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    tests = [
        ("模块导入测试", test_imports),
        ("文件结构检查", test_file_structure),
        ("UI组件测试", test_ui_components),
        ("主题管理器测试", test_theme_manager),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print('='*60)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}异常: {e}")
            results.append((test_name, False))

    # 显示总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print('='*60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！UI重构结构完整。")
        print("\n💡 下一步:")
        print("  1. 安装PySide6: pip install PySide6==6.8.0")
        print("  2. 运行启动器: python start_qt_ui.py")
        print("  3. 体验全新界面!")
        return True
    else:
        print("⚠️  存在问题，需要修复后再测试。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)