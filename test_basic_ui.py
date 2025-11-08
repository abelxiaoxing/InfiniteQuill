#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础UI测试
测试核心PySide6组件的基本功能
"""

import sys
import os

def test_basic_pyside6():
    """测试基础PySide6功能"""
    print("🔍 测试基础PySide6功能...")

    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
        from PySide6.QtCore import Qt, Signal
        from PySide6.QtGui import QFont
        print("  ✅ 基础组件导入成功")

        # 创建应用
        app = QApplication([])
        print("  ✅ QApplication创建成功")

        # 创建简单窗口
        window = QMainWindow()
        window.setWindowTitle("PySide6测试窗口")
        window.setGeometry(100, 100, 400, 300)
        print("  ✅ QMainWindow创建成功")

        # 创建中央控件
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # 添加标签和按钮
        label = QLabel("🎉 PySide6界面重构成功！")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 16))
        layout.addWidget(label)

        button = QPushButton("关闭")
        button.clicked.connect(window.close)
        layout.addWidget(button)

        window.setCentralWidget(central_widget)
        print("  ✅ 界面布局创建成功")

        # 显示窗口
        window.show()
        print("  ✅ 窗口显示成功")

        # 自动关闭测试
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, app.quit)

        print("  ⏰ 2秒后自动关闭...")
        app.exec()

        return True

    except Exception as e:
        print(f"  ❌ 基础测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_qt_modules():
    """测试UI模块导入"""
    print("\n🔍 测试UI模块导入...")

    modules_to_test = [
        ("主题管理器", "ui_qt.utils.theme_manager", "ThemeManager"),
        ("状态栏组件", "ui_qt.widgets.status_bar", "StatusBar"),
        ("配置组件", "ui_qt.widgets.config_widget", "ConfigWidget"),
        ("生成组件", "ui_qt.widgets.generation_widget", "GenerationWidget"),
        ("章节编辑器", "ui_qt.widgets.chapter_editor", "ChapterEditor"),
        ("角色管理器", "ui_qt.widgets.role_manager", "RoleManager"),
    ]

    success_count = 0
    for name, module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {name}导入成功")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {name}导入失败: {e}")

    print(f"\n📊 模块导入结果: {success_count}/{len(modules_to_test)} 成功")
    return success_count == len(modules_to_test)

def test_theme_system():
    """测试主题系统"""
    print("\n🎨 测试主题系统...")

    try:
        from ui_qt.utils.theme_manager import ThemeManager
        theme_manager = ThemeManager()

        # 测试主题样式生成
        light_theme = theme_manager.get_light_theme()
        dark_theme = theme_manager.get_dark_theme()

        if len(light_theme) > 1000 and len(dark_theme) > 1000:
            print("  ✅ 主题样式生成成功")
            return True
        else:
            print("  ❌ 主题样式生成失败")
            return False

    except Exception as e:
        print(f"  ❌ 主题系统测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                基础PySide6功能测试                        ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    tests = [
        ("基础PySide6功能", test_basic_pyside6),
        ("UI模块导入", test_ui_qt_modules),
        ("主题系统", test_theme_system),
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
        print("\n🎉 所有测试通过！PySide6界面准备就绪。")
        print("\n💡 下一步:")
        print("  1. 运行主程序: python3 main_qt.py")
        print("  2. 体验全新界面")
        print("  3. 如果遇到问题，查看错误日志")
        return True
    else:
        print("\n⚠️  部分测试失败，但基础功能可用。")
        print("\n💡 建议:")
        print("  1. 仍可尝试运行主程序")
        print("  2. 如遇问题，请查看具体错误")
        print("  3. 逐步修复失败的功能模块")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)