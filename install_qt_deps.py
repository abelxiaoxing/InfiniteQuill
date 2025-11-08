#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能PySide6依赖安装器
支持多种安装方法，确保成功安装PySide6
"""

import subprocess
import sys
import os

def check_pip():
    """检查pip是否可用"""
    try:
        import pip
        print(f"✅ pip可用，版本: {pip.__version__}")
        return True
    except ImportError:
        print("❌ pip不可用")
        return False

def check_pyside6():
    """检查PySide6是否已安装"""
    try:
        import PySide6
        print(f"✅ PySide6已安装，版本: {PySide6.__version__}")
        return True
    except ImportError:
        print("❌ PySide6未安装")
        return False

def install_with_pip(package, index=None):
    """使用pip安装包"""
    cmd = [sys.executable, "-m", "pip", "install"]
    if index:
        cmd.extend(["-i", index])
    cmd.append(package)

    print(f"🔧 执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {package} 安装成功")
            return True
        else:
            print(f"❌ {package} 安装失败:")
            print(f"错误输出: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {package} 安装超时")
        return False
    except Exception as e:
        print(f"❌ {package} 安装异常: {e}")
        return False

def install_with_uv(package):
    """尝试使用uv安装"""
    try:
        cmd = ["uv", "add", package]
        print(f"🔧 尝试uv安装: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0
    except:
        return False

def main():
    """主安装函数"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║              智能PySide6依赖安装器                      ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 检查当前状态
    print("🔍 检查当前环境...")
    pip_available = check_pip()
    pyside6_installed = check_pyside6()

    if pyside6_installed:
        print("🎉 PySide6已安装，无需重复安装")
        return True

    if not pip_available:
        print("❌ pip不可用，无法安装依赖")
        return False

    # 尝试不同的安装源和方法
    sources = [
        ("清华大学镜像", "https://pypi.tuna.tsinghua.edu.cn/simple/", None),
        ("阿里云镜像", "https://mirrors.aliyun.com/pypi/simple/", None),
        ("豆瓣源", "https://pypi.douban.com/simple/", None),
        ("华为源", "https://mirrors.huaweicloud.com/repository/pypi/simple/", None),
        ("官方源", "https://pypi.org/simple/", None),
    ]

    packages = [
        "PySide6==6.8.0",
        "PySide6==6.6.0",  # 回退版本
        "PySide6",         # 最新版本
    ]

    print("\n🚀 开始安装尝试...")

    for source_name, source_url, _ in sources:
        print(f"\n📡 尝试{source_name}...")

        for package in packages:
            print(f"  📦 安装 {package}")

            if source_url:
                success = install_with_pip(package, source_url)
            else:
                success = install_with_pip(package)

            if success:
                # 验证安装
                if check_pyside6():
                    print(f"\n🎉 成功！通过{source_name}安装了{package}")
                    return True

            print(f"  ⚠️  {package} 在{source_name}安装失败")

    # 尝试uv
    print("\n🔄 尝试使用uv安装...")
    for package in packages:
        if install_with_uv(package):
            if check_pyside6():
                print("🎉 成功！通过uv安装了PySide6")
                return True

    print("\n❌ 所有安装方法都失败了")
    print("\n💡 建议:")
    print("1. 检查网络连接")
    print("2. 尝试使用代理")
    print("3. 手动下载wheel文件安装")
    print("4. 使用系统包管理器")

    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)