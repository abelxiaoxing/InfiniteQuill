# project_manager.py
# -*- coding: utf-8 -*-
"""
项目管理系统
负责项目的创建、保存、加载和状态管理
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from utils import save_data_to_json, read_file, load_data_from_json

logger = logging.getLogger(__name__)

class ProjectManager:
    """项目管理器"""

    PROJECT_CONFIG_FILE = "project.json"  # 项目配置文件名

    def __init__(self):
        self.current_project_path = None
        self.project_data = None

    def create_project(self, project_path: str, project_info: Dict[str, Any]) -> bool:
        """
        创建新项目

        Args:
            project_path: 项目根目录路径
            project_info: 项目基本信息

        Returns:
            bool: 创建是否成功
        """
        try:
            # 创建项目目录结构
            os.makedirs(project_path, exist_ok=True)
            os.makedirs(os.path.join(project_path, "chapters"), exist_ok=True)

            # 准备项目数据
            project_data = {
                "project_info": {
                    "name": project_info.get("name", "未命名项目"),
                    "title": project_info.get("title", ""),
                    "topic": project_info.get("topic", ""),
                    "genre": project_info.get("genre", "玄幻"),
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "settings": {
                    "chapter_count": project_info.get("chapter_count", 20),
                    "word_count": project_info.get("word_count", 3000),
                    "worldview": project_info.get("worldview", ""),
                    "writing_style": project_info.get("writing_style", "简洁明快"),
                    "target_readers": project_info.get("target_readers", "全年龄"),
                    "save_path": project_path
                },
                "generation_status": {
                    "architecture_generated": False,
                    "blueprint_generated": False,
                    "generated_chapters": [],  # 已生成的章节号列表
                    "total_words": 0,
                    "last_chapter": 0
                },
                "files": {
                    "architecture_file": "Novel_architecture.txt",
                    "blueprint_file": "Novel_directory.txt",
                    "summary_file": "global_summary.txt",
                    "character_state_file": "character_state.txt",
                    "chapters_dir": "chapters"
                },
                "ui_state": {
                    "selected_chapter": 1,
                    "active_tab": 0
                }
            }

            # 保存项目配置文件
            config_path = os.path.join(project_path, self.PROJECT_CONFIG_FILE)
            if not save_data_to_json(project_data, config_path):
                logger.error("项目配置文件保存失败")
                return False

            self.current_project_path = project_path
            self.project_data = project_data

            logger.info(f"项目创建成功: {project_path}")
            return True

        except Exception as e:
            logger.error(f"创建项目时发生错误: {str(e)}", exc_info=True)
            return False

    def save_project(self, project_path: str, project_data: Dict[str, Any]) -> bool:
        """
        保存项目数据

        Args:
            project_path: 项目路径
            project_data: 项目数据

        Returns:
            bool: 保存是否成功
        """
        try:
            # 更新最后修改时间
            if "project_info" in project_data:
                project_data["project_info"]["last_modified"] = datetime.now().isoformat()

            # 保存到配置文件
            config_path = os.path.join(project_path, self.PROJECT_CONFIG_FILE)
            if not save_data_to_json(project_data, config_path):
                logger.error("项目保存失败")
                return False

            self.current_project_path = project_path
            self.project_data = project_data

            logger.info(f"项目已保存: {project_path}")
            return True

        except Exception as e:
            logger.error(f"保存项目时发生错误: {str(e)}", exc_info=True)
            return False

    def load_project(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        加载项目

        Args:
            project_path: 项目路径

        Returns:
            Optional[Dict]: 项目数据，失败返回None
        """
        try:
            # 检查项目配置文件是否存在
            config_path = os.path.join(project_path, self.PROJECT_CONFIG_FILE)
            if not os.path.exists(config_path):
                logger.error(f"项目配置文件不存在: {config_path}")
                return None

            # 读取项目配置
            project_data = load_data_from_json(config_path)
            if project_data is None:
                logger.error(f"读取项目配置文件失败: {config_path}")
                return None

            # 验证项目数据完整性
            if not self._validate_project_data(project_data):
                logger.error("项目数据验证失败")
                return None

            self.current_project_path = project_path
            self.project_data = project_data

            logger.info(f"项目加载成功: {project_path}")
            return project_data

        except Exception as e:
            logger.error(f"加载项目时发生错误: {str(e)}", exc_info=True)
            return None

    def _validate_project_data(self, data: Dict[str, Any]) -> bool:
        """验证项目数据完整性"""
        required_keys = ["project_info", "settings", "generation_status", "files"]
        for key in required_keys:
            if key not in data:
                logger.error(f"项目数据缺少必要字段: {key}")
                return False
        return True

    def update_generation_status(self, chapter_num: int, is_completed: bool = True):
        """更新生成状态"""
        if not self.project_data:
            return

        try:
            status = self.project_data["generation_status"]

            # 更新已生成章节列表
            if is_completed and chapter_num not in status["generated_chapters"]:
                status["generated_chapters"].append(chapter_num)
                status["generated_chapters"].sort()
                status["last_chapter"] = max(status["generated_chapters"])

            # 更新架构和蓝图生成状态
            architecture_file = os.path.join(
                self.current_project_path,
                self.project_data["files"]["architecture_file"]
            )
            if os.path.exists(architecture_file):
                status["architecture_generated"] = True

            blueprint_file = os.path.join(
                self.current_project_path,
                self.project_data["files"]["blueprint_file"]
            )
            if os.path.exists(blueprint_file):
                status["blueprint_generated"] = True

            # 重新计算总字数
            status["total_words"] = self._calculate_total_words()

            # 保存更新
            self.save_project(self.current_project_path, self.project_data)

        except Exception as e:
            logger.error(f"更新生成状态失败: {str(e)}", exc_info=True)

    def _calculate_total_words(self) -> int:
        """计算所有章节的总字数"""
        if not self.current_project_path or not self.project_data:
            return 0

        try:
            total_words = 0
            chapters_dir = os.path.join(
                self.current_project_path,
                self.project_data["files"]["chapters_dir"]
            )

            if not os.path.exists(chapters_dir):
                return 0

            for filename in os.listdir(chapters_dir):
                if filename.endswith('.txt'):
                    chapter_path = os.path.join(chapters_dir, filename)
                    content = read_file(chapter_path)
                    total_words += len(content)

            return total_words

        except Exception as e:
            logger.error(f"计算总字数失败: {str(e)}")
            return 0

    def get_current_project(self) -> Optional[str]:
        """获取当前项目路径"""
        return self.current_project_path

    def get_project_data(self) -> Optional[Dict[str, Any]]:
        """获取当前项目数据"""
        return self.project_data

    def export_project_summary(self) -> str:
        """导出项目摘要"""
        if not self.project_data:
            return "无项目数据"

        try:
            info = self.project_data["project_info"]
            status = self.project_data["generation_status"]
            settings = self.project_data["settings"]

            summary = f"""
项目名称: {info.get('name', '未命名')}
小说标题: {info.get('title', '未设置')}
体裁: {info.get('genre', '未设置')}
章节数: {settings.get('chapter_count', 0)}
目标字数: {settings.get('word_count', 0)}/章

生成状态:
  - 架构: {'✓' if status.get('architecture_generated') else '✗'}
  - 蓝图: {'✓' if status.get('blueprint_generated') else '✗'}
  - 已生成章节: {', '.join(map(str, status.get('generated_chapters', [])))}
  - 总字数: {status.get('total_words', 0)}

创建时间: {info.get('created_at', '未知')}
最后修改: {info.get('last_modified', '未知')}
            """.strip()

            return summary

        except Exception as e:
            logger.error(f"导出项目摘要失败: {str(e)}")
            return "导出失败"

    def is_valid_project(self, project_path: str) -> bool:
        """检查路径是否为有效项目"""
        config_path = os.path.join(project_path, self.PROJECT_CONFIG_FILE)
        return os.path.exists(config_path)
