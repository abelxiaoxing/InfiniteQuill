# novel_generator/data_manager.py
# -*- coding: utf-8 -*-
"""
数据管理模块
负责项目数据的持久化存储和读取
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DataManager:
    """项目数据管理器"""

    def __init__(self, project_path: str):
        """
        初始化数据管理器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.chapters_dir = self.project_path / "chapters"
        self.config_file = self.project_path / "project.json"
        self.architecture_file = self.project_path / "architecture.md"
        self.blueprint_file = self.project_path / "blueprint.md"
        self.summary_file = self.project_path / "summary.txt"
        self.roles_file = self.project_path / "roles.json"

        # 确保项目目录结构存在
        self._ensure_project_structure()

    def _ensure_project_structure(self):
        """确保项目目录结构存在"""
        try:
            # 创建必要的目录
            self.chapters_dir.mkdir(parents=True, exist_ok=True)

            # 创建必要的文件（如果不存在）
            if not self.config_file.exists():
                self._create_default_config()

            if not self.roles_file.exists():
                self._create_default_roles()

            logger.info(f"项目目录结构已初始化: {self.project_path}")

        except Exception as e:
            logger.error(f"创建项目目录结构失败: {e}")
            raise

    def _create_default_config(self):
        """创建默认的项目配置"""
        default_config = {
            "name": "未命名项目",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "chapters": [],
            "word_count": 0,
            "settings": {
                "genre": "玄幻",
                "target_chapters": 20,
                "words_per_chapter": 3000
            }
        }
        self.save_project_config(default_config)

    def _create_default_roles(self):
        """创建默认的角色文件"""
        default_roles = {}
        self.save_roles(default_roles)

    # ========== 项目配置管理 ==========

    def load_project_config(self) -> Dict[str, Any]:
        """加载项目配置"""
        try:
            if not self.config_file.exists():
                logger.warning(f"项目配置文件不存在: {self.config_file}")
                return {}

            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"项目配置已加载: {self.config_file}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"项目配置文件JSON格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载项目配置失败: {e}")
            raise

    def save_project_config(self, config: Dict[str, Any]):
        """保存项目配置"""
        try:
            # 更新修改时间
            config["updated"] = datetime.now().isoformat()

            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"项目配置已保存: {self.config_file}")

        except Exception as e:
            logger.error(f"保存项目配置失败: {e}")
            raise

    # ========== 章节管理 ==========

    def load_chapter(self, chapter_number: int) -> str:
        """
        加载指定章节内容

        Args:
            chapter_number: 章节编号

        Returns:
            章节内容字符串
        """
        try:
            chapter_file = self.chapters_dir / f"chapter_{chapter_number:03d}.md"

            if not chapter_file.exists():
                logger.warning(f"章节文件不存在: {chapter_file}")
                return ""

            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.debug(f"章节 {chapter_number} 已加载")
            return content

        except Exception as e:
            logger.error(f"加载章节 {chapter_number} 失败: {e}")
            raise

    def save_chapter(self, chapter_number: int, content: str, title: str = ""):
        """
        保存指定章节内容

        Args:
            chapter_number: 章节编号
            content: 章节内容
            title: 章节标题
        """
        try:
            # 确保目录存在
            self.chapters_dir.mkdir(parents=True, exist_ok=True)

            chapter_file = self.chapters_dir / f"chapter_{chapter_number:03d}.md"

            # 如果有标题，添加到内容开头
            if title:
                content = f"# {title}\n\n{content}"

            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # 更新项目配置中的章节列表
            self._update_chapter_in_config(chapter_number, title)

            logger.info(f"章节 {chapter_number} 已保存: {chapter_file}")

        except Exception as e:
            logger.error(f"保存章节 {chapter_number} 失败: {e}")
            raise

    def delete_chapter(self, chapter_number: int):
        """
        删除指定章节

        Args:
            chapter_number: 章节编号
        """
        try:
            chapter_file = self.chapters_dir / f"chapter_{chapter_number:03d}.md"

            if chapter_file.exists():
                chapter_file.unlink()
                logger.info(f"章节文件已删除: {chapter_file}")

            # 从项目配置中移除
            self._remove_chapter_from_config(chapter_number)

        except Exception as e:
            logger.error(f"删除章节 {chapter_number} 失败: {e}")
            raise

    def list_chapters(self) -> List[int]:
        """
        列出所有章节编号

        Returns:
            章节编号列表
        """
        try:
            chapters = []
            for chapter_file in self.chapters_dir.glob("chapter_*.md"):
                # 提取章节编号
                filename = chapter_file.stem  # 不含扩展名
                try:
                    chapter_num = int(filename.split("_")[1])
                    chapters.append(chapter_num)
                except (IndexError, ValueError):
                    continue

            chapters.sort()
            logger.debug(f"发现 {len(chapters)} 个章节")
            return chapters

        except Exception as e:
            logger.error(f"列出章节失败: {e}")
            return []

    def get_chapter_count(self) -> int:
        """获取章节数量"""
        return len(self.list_chapters())

    def _update_chapter_in_config(self, chapter_number: int, title: str):
        """更新项目配置中的章节信息"""
        try:
            config = self.load_project_config()
            chapters = config.get("chapters", [])

            # 查找章节是否已存在
            chapter_info = {
                "number": chapter_number,
                "title": title or f"第{chapter_number}章",
                "updated": datetime.now().isoformat()
            }

            # 检查章节是否已存在
            existing = next((c for c in chapters if c["number"] == chapter_number), None)

            if existing:
                # 更新现有章节
                existing.update(chapter_info)
            else:
                # 添加新章节
                chapters.append(chapter_info)

            # 按章节号排序
            chapters.sort(key=lambda x: x["number"])

            # 重新计算总字数
            total_words = self._calculate_total_words()
            config["chapters"] = chapters
            config["word_count"] = total_words

            self.save_project_config(config)

        except Exception as e:
            logger.error(f"更新章节配置失败: {e}")

    def _remove_chapter_from_config(self, chapter_number: int):
        """从项目配置中移除章节信息"""
        try:
            config = self.load_project_config()
            chapters = config.get("chapters", [])

            # 过滤掉指定章节
            chapters = [c for c in chapters if c["number"] != chapter_number]

            # 重新计算总字数
            total_words = self._calculate_total_words()
            config["chapters"] = chapters
            config["word_count"] = total_words

            self.save_project_config(config)

        except Exception as e:
            logger.error(f"移除章节配置失败: {e}")

    def _calculate_total_words(self) -> int:
        """计算项目总字数"""
        try:
            total_words = 0
            for chapter_number in self.list_chapters():
                content = self.load_chapter(chapter_number)
                # 简单字数统计（去除空白字符）
                words = len(content.replace(" ", "").replace("\n", ""))
                total_words += words
            return total_words
        except Exception as e:
            logger.error(f"计算总字数失败: {e}")
            return 0

    # ========== 架构管理 ==========

    def load_architecture(self) -> str:
        """加载小说架构"""
        try:
            if not self.architecture_file.exists():
                logger.warning(f"架构文件不存在: {self.architecture_file}")
                return ""

            with open(self.architecture_file, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"小说架构已加载")
            return content

        except Exception as e:
            logger.error(f"加载小说架构失败: {e}")
            raise

    def save_architecture(self, content: str):
        """保存小说架构"""
        try:
            # 确保目录存在
            self.architecture_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.architecture_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"小说架构已保存: {self.architecture_file}")

        except Exception as e:
            logger.error(f"保存小说架构失败: {e}")
            raise

    # ========== 蓝图管理 ==========

    def load_blueprint(self) -> str:
        """加载章节蓝图"""
        try:
            if not self.blueprint_file.exists():
                logger.warning(f"蓝图文件不存在: {self.blueprint_file}")
                return ""

            with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"章节蓝图已加载")
            return content

        except Exception as e:
            logger.error(f"加载章节蓝图失败: {e}")
            raise

    def save_blueprint(self, content: str):
        """保存章节蓝图"""
        try:
            # 确保目录存在
            self.blueprint_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.blueprint_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"章节蓝图已保存: {self.blueprint_file}")

        except Exception as e:
            logger.error(f"保存章节蓝图失败: {e}")
            raise

    # ========== 概览管理 ==========

    def load_summary(self) -> str:
        """加载全局概览"""
        try:
            if not self.summary_file.exists():
                logger.warning(f"概览文件不存在: {self.summary_file}")
                return ""

            with open(self.summary_file, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"全局概览已加载")
            return content

        except Exception as e:
            logger.error(f"加载全局概览失败: {e}")
            raise

    def save_summary(self, content: str):
        """保存全局概览"""
        try:
            # 确保目录存在
            self.summary_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"全局概览已保存: {self.summary_file}")

        except Exception as e:
            logger.error(f"保存全局概览失败: {e}")
            raise

    # ========== 角色管理 ==========

    def load_roles(self) -> Dict[str, Any]:
        """加载角色数据"""
        try:
            if not self.roles_file.exists():
                logger.warning(f"角色文件不存在: {self.roles_file}")
                return {}

            with open(self.roles_file, 'r', encoding='utf-8') as f:
                roles = json.load(f)

            logger.info(f"角色数据已加载，共 {len(roles)} 个角色")
            return roles

        except json.JSONDecodeError as e:
            logger.error(f"角色文件JSON格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载角色数据失败: {e}")
            raise

    def save_roles(self, roles: Dict[str, Any]):
        """保存角色数据"""
        try:
            # 确保目录存在
            self.roles_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.roles_file, 'w', encoding='utf-8') as f:
                json.dump(roles, f, ensure_ascii=False, indent=2)

            logger.info(f"角色数据已保存，共 {len(roles)} 个角色")

        except Exception as e:
            logger.error(f"保存角色数据失败: {e}")
            raise

    # ========== 工具方法 ==========

    def get_project_info(self) -> Dict[str, Any]:
        """获取项目基本信息"""
        try:
            config = self.load_project_config()
            chapters = self.list_chapters()
            roles = self.load_roles()

            return {
                "name": config.get("name", "未命名项目"),
                "created": config.get("created", ""),
                "updated": config.get("updated", ""),
                "chapter_count": len(chapters),
                "word_count": config.get("word_count", 0),
                "role_count": len(roles),
                "project_path": str(self.project_path)
            }

        except Exception as e:
            logger.error(f"获取项目信息失败: {e}")
            return {}

    def export_project(self, export_path: str):
        """
        导出整个项目

        Args:
            export_path: 导出目标路径
        """
        try:
            import shutil
            export_dir = Path(export_path)

            if export_dir.exists():
                shutil.rmtree(export_dir)

            # 复制整个项目目录
            shutil.copytree(self.project_path, export_dir)
            logger.info(f"项目已导出到: {export_path}")

        except Exception as e:
            logger.error(f"导出项目失败: {e}")
            raise

    def backup_project(self, backup_dir: Optional[str] = None) -> str:
        """
        备份项目

        Args:
            backup_dir: 备份目录，默认在项目目录下创建backup文件夹

        Returns:
            备份文件路径
        """
        try:
            if backup_dir is None:
                backup_dir = self.project_path / "backup"
            else:
                backup_dir = Path(backup_dir)

            # 创建带时间戳的备份文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"

            # 复制项目文件
            import shutil
            shutil.copytree(self.project_path, backup_path)

            logger.info(f"项目已备份到: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"备份项目失败: {e}")
            raise
