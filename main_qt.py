#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI小说生成器 - PySide6版本主入口
现代化的桌面应用程序界面
"""

import sys
import os
import logging
from pathlib import Path

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入PySide6模块
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale
from PySide6.QtGui import QIcon

# 导入自定义模块
from ui_qt import setup_application, MainWindow
from config_manager import load_config

# 设置日志
def setup_logging():
    """设置日志系统"""
    log_file = PROJECT_ROOT / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("AI小说生成器启动中...")
    return logger

def setup_translator(app: QApplication):
    """设置国际化翻译器"""
    translator = QTranslator()
    locale = QLocale.system().name()

    # 尝试加载翻译文件
    translation_file = PROJECT_ROOT / "translations" / f"app_{locale}.qm"
    if translation_file.exists():
        translator.load(str(translation_file))
        app.installTranslator(translator)
        logging.info(f"已加载翻译文件: {translation_file}")
    else:
        logging.info("使用默认语言（中文简体）")

def check_dependencies():
    """检查依赖项"""
    required_modules = [
        'PySide6', 'chromadb', 'langchain', 'openai',
        'transformers', 'torch', 'sentence_transformers'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        logging.error(f"缺少依赖模块: {', '.join(missing_modules)}")
        print(f"\n[错误] 缺少依赖模块: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False

    return True

def show_startup_info():
    """显示启动信息"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    AI小说生成器 v2.0                         ║
    ║                PySide6现代化界面版本                          ║
    ╚══════════════════════════════════════════════════════════════╝

    界面特性:
    • 完美的中文显示支持
    • 现代化Material Design风格
    • 高性能Qt渲染引擎
    • 响应式布局设计

    核心功能:
    • 多LLM服务支持 (OpenAI/DeepSeek/Gemini等)
    • 智能小说架构生成
    • 章节内容自动创作
    • 向量检索确保连贯性
    • 角色关系管理

    技术栈:
    • PySide6 - 现代化GUI框架
    • LangChain - LLM应用框架
    • ChromaDB - 向量数据库
    • Transformers - AI模型库
    """)

def main():
    """主函数"""
    try:
        # 显示启动信息
        show_startup_info()

        # 设置日志
        logger = setup_logging()

        # 检查依赖
        if not check_dependencies():
            sys.exit(1)

        # 创建QApplication
        app = setup_application()
        logger.info("应用程序实例创建完成")

        # 设置国际化
        setup_translator(app)

        # 加载配置
        config = load_config("config.json") or {}
        logger.info(f"配置加载完成: {len(config)} 个配置项")

        # 创建主窗口
        main_window = MainWindow()
        logger.info("主窗口创建完成")

        # 显示主窗口
        main_window.show()

        # 如果有启动错误，在状态栏显示
        if not config:
            main_window.status_bar.set_warning_state("未找到配置文件，请检查config.json")

        # 启动应用程序事件循环
        logger.info("应用程序启动成功，进入事件循环")

        # 设置异常处理
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            error_msg = f"未捕获的异常: {exc_type.__name__}: {exc_value}"
            logger.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))

            # 在主窗口显示错误（如果窗口还存在）
            try:
                if main_window.isVisible():
                    main_window.status_bar.set_error_state(f"程序异常: {exc_type.__name__}")
            except:
                pass

        sys.excepthook = handle_exception

        # 运行应用程序
        exit_code = app.exec()

        logger.info(f"应用程序退出，退出代码: {exit_code}")
        return exit_code

    except Exception as e:
        print(f"[错误] 启动失败: {str(e)}")
        logging.exception("应用程序启动失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())