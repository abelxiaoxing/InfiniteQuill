#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序测试
直接测试PySide6界面启动
"""

import sys
import os

def test_main_qt():
    """测试主程序"""
    print("🔍 测试PySide6主程序...")

    try:
        # 导入并运行主程序
        import main_qt
        print("✅ main_qt模块导入成功")
        return True

    except Exception as e:
        print(f"❌ 主程序测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_app():
    """测试简单应用"""
    print("\n🧪 测试简单PySide6应用...")

    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QFont

        app = QApplication([])
        print("  ✅ QApplication创建成功")

        window = QMainWindow()
        window.setWindowTitle("PySide6测试")
        window.setGeometry(100, 100, 500, 300)
        print("  ✅ QMainWindow创建成功")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        label = QLabel("🎉 PySide6界面重构成功！\n中文显示完美！")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Microsoft YaHei UI", 14))
        layout.addWidget(label)

        button = QPushButton("测试完成，点击关闭")
        button.clicked.connect(app.quit)
        layout.addWidget(button)

        window.setCentralWidget(central_widget)
        window.show()
        print("  ✅ 界面显示成功")

        # 3秒后自动关闭
        QTimer.singleShot(3000, app.quit)

        app.exec()
        print("  ✅ 应用运行成功")
        return True

    except Exception as e:
        print(f"  ❌ 简单应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                  PySide6界面测试工具                  ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # 测试简单应用
    simple_success = test_simple_app()

    # 测试主程序
    main_success = test_main_qt()

    print(f"\n📊 测试结果:")
    print(f"  简单应用: {'✅ 成功' if simple_success else '❌ 失败'}")
    print(f"  主程序测试: {'✅ 成功' if main_success else '❌ 失败'}")

    if simple_success:
        print("\n🎉 基础PySide6功能正常！")
        print("\n💡 运行新界面的方法:")
        print("  1. python3 main_qt.py")
        print("  2. 如果有问题，查看错误信息")
        return True
    else:
        print("\n⚠️  基础功能有问题，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)