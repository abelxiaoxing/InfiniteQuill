#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题和emoji显示测试
验证深色模式和emoji表情的正确显示
"""

import sys
import os
sys.path.append('.')

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QGroupBox, QHBoxLayout, QTabWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ui_qt.utils.theme_manager import ThemeManager

def create_test_window():
    """创建测试窗口"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("🎨 主题和Emoji测试")
    window.setGeometry(100, 100, 600, 400)

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    # 标题
    title_label = QLabel("🎉 PySide6界面重构成功！")
    title_label.setAlignment(Qt.AlignCenter)
    title_font = QFont()
    title_font.setPointSize(16)
    title_font.setBold(True)
    title_label.setFont(title_font)
    layout.addWidget(title_label)

    # 测试emoji
    emoji_group = QGroupBox("🔤 Emoji表情测试")
    emoji_layout = QVBoxLayout(emoji_group)

    emoji_tests = [
        "✅ 成功",
        "❌ 失败",
        "⚠️ 警告",
        "🚀 启动",
        "💾 保存",
        "⚙️ 设置",
        "🎨 界面",
        "👥 角色",
        "📝 编辑",
        "🔄 重载",
        "🎯 目标",
        "💡 提示",
        "🔍 搜索",
        "📁 文件夹",
        "📤 导出",
        "🔗 链接",
        "💬 评论",
        "🌟 星星",
        "🌙 月亮",
        "☀️ 太阳"
    ]

    for emoji_text in emoji_tests:
        label = QLabel(emoji_text)
        label.setMinimumHeight(25)
        emoji_layout.addWidget(label)

    layout.addWidget(emoji_group)

    # 功能测试区域
    feature_group = QGroupBox("🎨 功能特色")
    feature_layout = QVBoxLayout(feature_group)

    features = [
        "• 🎭 完美中文显示支持",
        "• ⚡ 极致性能表现",
        "• 🌗 深浅主题切换",
        "• 🎨 Material Design风格",
        "• 📱 响应式布局设计",
        "• 🧩 模块化组件架构",
        "• 🔄 异步任务处理",
        "• 🎯 错误处理机制"
    ]

    for feature in features:
        label = QLabel(feature)
        label.setMinimumHeight(25)
        feature_layout.addWidget(label)

    layout.addWidget(feature_group)

    # 主题切换按钮
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)

    theme_manager = ThemeManager()

    light_btn = QPushButton("☀️ 浅色主题")
    dark_btn = QPushButton("🌙 深色主题")

    def switch_to_light():
        theme_manager.apply_theme(window, "light")

    def switch_to_dark():
        theme_manager.apply_theme(window, "dark")

    light_btn.clicked.connect(switch_to_light)
    dark_btn.clicked.connect(switch_to_dark)

    button_layout.addWidget(light_btn)
    button_layout.addWidget(dark_btn)

    layout.addWidget(button_widget)

    window.setCentralWidget(central_widget)

    return app, window

def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                主题和Emoji显示测试工具                   ║
    ╚════════════════════════════════════════════════════════╝
    """)

    try:
        app, window = create_test_window()

        print("✅ 测试窗口创建成功")
        print("🎨 测试内容:")
        print("  • Emoji表情显示")
        print("  • 深浅主题切换")
        print("  • 中文字体渲染")
        print("  • 字体颜色协调")

        window.show()
        print("✅ 窗口显示成功")

        # 自动关闭测试
        QTimer.singleShot(8000, app.quit)
        print("⏰ 8秒后自动关闭")

        # 设置默认深色主题
        theme_manager = ThemeManager()
        theme_manager.apply_theme(window, "dark")
        print("🌙 已应用深色主题")

        # 2秒后切换到浅色主题
        def switch_theme():
            theme_manager.apply_theme(window, "light")
            print("☀️ 已切换到浅色主题")

            # 2秒后再切回深色
            def switch_back():
                theme_manager.apply_theme(window, "dark")
                print("🌙 已切换回深色主题")

            QTimer.singleShot(2000, switch_back)

        QTimer.singleShot(2000, switch_theme)

        print("\n🎬 开始界面测试...")
        app.exec()

        print("✅ 测试完成！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)