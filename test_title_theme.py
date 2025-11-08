#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题主题测试
专门测试"小说生成操作"标题在不同主题下的显示效果
"""

import sys
import os
sys.path.append('.')

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ui_qt.utils.theme_manager import ThemeManager
from ui_qt.widgets.generation_widget import GenerationWidget

def test_title_theme():
    """测试标题主题效果"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                标题主题测试工具                        ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("🎨 标题主题测试")
    window.setGeometry(100, 100, 500, 600)

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    # 说明
    info_label = QLabel("📋 测试'小说生成操作'标题在不同主题下的效果")
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setMinimumHeight(40)
    layout.addWidget(info_label)

    # 创建生成组件
    config = {"theme": "light"}
    generation_widget = GenerationWidget(config, window)
    layout.addWidget(generation_widget)

    # 主题切换按钮
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)

    theme_manager = ThemeManager()

    def switch_to_light():
        theme_manager.apply_theme(window, "light")
        generation_widget.update_component_themes("light")
        print("☀️ 已切换到浅色主题")

    def switch_to_dark():
        theme_manager.apply_theme(window, "dark")
        generation_widget.update_component_themes("dark")
        print("🌙 已切换到深色主题")

    def test_title():
        # 显示当前标题样式信息
        current_theme = config.get("theme", "light")
        title_stylesheet = generation_widget.title_label.styleSheet()

        print(f"\n🎨 当前主题: {current_theme}")
        print(f"📝 标题样式:")
        print(title_stylesheet)
        print("="*50)

    light_btn = QPushButton("☀️ 浅色主题")
    dark_btn = QPushButton("🌙 深色主题")
    test_btn = QPushButton("🎯 查看标题样式")

    light_btn.clicked.connect(switch_to_light)
    dark_btn.clicked.connect(switch_to_dark)
    test_btn.clicked.connect(test_title)

    button_layout.addWidget(light_btn)
    button_layout.addWidget(dark_btn)
    button_layout.addWidget(test_btn)

    layout.addWidget(button_widget)

    window.setCentralWidget(central_widget)

    # 显示窗口
    window.show()

    # 自动主题切换测试
    def auto_switch():
        print("\n🔄 开始自动主题切换测试...")

        # 切换到深色
        switch_to_dark()

        # 2秒后切换到浅色
        QTimer.singleShot(2000, switch_to_light)

        # 2秒后切换回深色
        QTimer.singleShot(4000, switch_to_dark)

        # 2秒后切换到浅色
        QTimer.singleShot(6000, switch_to_light)

        # 查看最终样式
        QTimer.singleShot(8000, test_title)

        # 10秒后关闭
        QTimer.singleShot(10000, app.quit)
        print("⏰ 10秒后自动关闭")

    print("✅ 窗口创建成功")
    print("🔄 3秒后开始自动主题切换测试...")

    # 3秒后开始自动测试
    QTimer.singleShot(3000, auto_switch)

    app.exec()

    print("✅ 测试完成！")
    return True

if __name__ == "__main__":
    success = test_title_theme()
    sys.exit(0 if success else 1)