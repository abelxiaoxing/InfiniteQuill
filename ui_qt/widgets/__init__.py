# ui_qt/widgets/__init__.py
# -*- coding: utf-8 -*-
"""
自定义UI组件模块
提供可复用的界面组件
"""

from .config_widget import ConfigWidget
from .generation_widget import GenerationWidget
from .chapter_editor import ChapterEditor
from .role_manager import RoleManager
from .status_bar import StatusBar

__all__ = [
    'ConfigWidget',
    'GenerationWidget',
    'ChapterEditor',
    'RoleManager',
    'StatusBar'
]