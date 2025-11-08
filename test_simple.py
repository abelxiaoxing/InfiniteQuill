#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版UI测试
在没有PySide6的情况下测试UI结构
"""

import sys
import os

def test_structure():
    """测试UI结构完整性"""
    print("🔍 测试UI文件结构...")

    required_files = [
        "ui_qt/__init__.py",
        "ui_qt/main_window.py",
        "ui_qt/widgets/__init__.py",
        "ui_qt/widgets/config_widget.py",
        "ui_qt/utils/__init__.py",
        "ui_qt/utils/theme_manager.py"
    ]

    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing.append(file_path)

    return len(missing) == 0

def test_python_syntax():
    """测试Python语法正确性"""
    print("\n🧪 测试Python语法...")

    python_files = []
    for root, dirs, files in os.walk("ui_qt"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # 添加主要文件
    python_files.extend(["main_qt.py", "start_qt_ui.py"])

    errors = []
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                print(f"  ✅ {file_path}")
            except SyntaxError as e:
                print(f"  ❌ {file_path}: {e}")
                errors.append((file_path, str(e)))
            except Exception as e:
                print(f"  ⚠️  {file_path}: {e}")

    return len(errors) == 0

def main():
    """主测试函数"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║              简化版UI结构测试工具                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    structure_ok = test_structure()
    syntax_ok = test_python_syntax()

    print(f"\n📊 测试结果:")
    print(f"  结构测试: {'✅ 通过' if structure_ok else '❌ 失败'}")
    print(f"  语法测试: {'✅ 通过' if syntax_ok else '❌ 失败'}")

    if structure_ok and syntax_ok:
        print("\n🎉 基础结构测试通过！")
        print("💡 下一步:")
        print("  1. 安装PySide6: pip install PySide6")
        print("  2. 运行完整测试: python test_ui_structure.py")
        print("  3. 启动新界面: python main_qt.py")
        return True
    else:
        print("\n⚠️  存在问题，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)