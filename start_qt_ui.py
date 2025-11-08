#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动PySide6界面的快速脚本
用于测试新的现代化界面
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_pyside6():
    """检查PySide6是否安装"""
    try:
        import PySide6
        print(f"✅ PySide6已安装 (版本: {PySide6.__version__})")
        return True
    except ImportError:
        print("❌ PySide6未安装")
        print("请运行: pip install PySide6==6.8.0")
        return False

def check_existing_ui():
    """检查现有UI依赖"""
    try:
        import customtkinter
        print("⚠️  检测到现有的customtkinter界面")
        return True
    except ImportError:
        print("ℹ️  未检测到customtkinter界面")
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 正在安装PySide6依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "PySide6==6.8.0", "PySide6-Addons==6.8.0"
        ])
        print("✅ PySide6依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def create_backup():
    """创建现有文件的备份"""
    if os.path.exists("main.py"):
        import shutil
        backup_name = "main_tkinter_backup.py"
        shutil.copy("main.py", backup_name)
        print(f"📁 已备份原始主文件: {backup_name}")
        return True
    return False

def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║              AI小说生成器 - PySide6界面启动器              ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # 检查Python版本
    if not check_python_version():
        sys.exit(1)

    # 检查现有界面
    check_existing_ui()

    # 检查PySide6
    if not check_pyside6():
        install_choice = input("是否安装PySide6依赖? (y/n): ").lower().strip()
        if install_choice in ['y', 'yes', '是']:
            if not install_dependencies():
                sys.exit(1)
        else:
            print("❌ 取消启动")
            sys.exit(1)

    # 创建备份
    create_backup()

    print("\n🚀 启动PySide6界面...")
    print("=" * 60)

    try:
        # 启动新的PySide6界面
        os.execv(sys.executable, [sys.executable, "main_qt.py"])
    except FileNotFoundError:
        print("❌ 找不到main_qt.py文件")
        print("请确保在AI小说生成器根目录下运行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()