# novel_generator/project_manager.py
# -*- coding: utf-8 -*-
"""
项目管理模块
负责项目的创建、加载、初始化和管理
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .data_manager import DataManager

logger = logging.getLogger(__name__)


class ProjectManager:
    """项目管理器"""

    def __init__(self, project_path: Optional[str] = None):
        """
        初始化项目管理器

        Args:
            project_path: 项目路径，如果为None则不加载项目
        """
        self.project_path = None
        self.data_manager = None
        self.is_project_loaded = False

        if project_path:
            self.load_project(project_path)

    def create_project(self, project_path: str, project_name: str = "未命名项目") -> bool:
        """
        创建新项目

        Args:
            project_path: 项目保存路径
            project_name: 项目名称

        Returns:
            创建是否成功
        """
        try:
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)

            # 初始化数据管理器
            self.data_manager = DataManager(str(project_dir))

            # 更新项目配置
            config = self.data_manager.load_project_config()
            config["name"] = project_name
            config["created"] = datetime.now().isoformat()
            self.data_manager.save_project_config(config)

            self.project_path = str(project_dir)
            self.is_project_loaded = True

            logger.info(f"项目已创建: {project_path}")
            return True

        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            return False

    def load_project(self, project_path: str) -> bool:
        """
        加载项目

        Args:
            project_path: 项目路径

        Returns:
            加载是否成功
        """
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                logger.error(f"项目目录不存在: {project_path}")
                return False

            if not (project_dir / "project.json").exists():
                logger.error(f"不是有效的项目目录: {project_path}")
                return False

            # 初始化数据管理器
            self.data_manager = DataManager(str(project_dir))
            self.project_path = str(project_dir)
            self.is_project_loaded = True

            logger.info(f"项目已加载: {project_path}")
            return True

        except Exception as e:
            logger.error(f"加载项目失败: {e}")
            return False

    def save_project(self) -> bool:
        """
        保存当前项目

        Returns:
            保存是否成功
        """
        try:
            if not self.is_project_loaded:
                logger.error("没有加载的项目")
                return False

            # 数据管理器会自动保存
            logger.info("项目已保存")
            return True

        except Exception as e:
            logger.error(f"保存项目失败: {e}")
            return False

    def close_project(self):
        """关闭当前项目"""
        self.project_path = None
        self.data_manager = None
        self.is_project_loaded = False
        logger.info("项目已关闭")

    def is_valid_project(self, project_path: str) -> bool:
        """
        检查路径是否为有效项目

        Args:
            project_path: 项目路径

        Returns:
            是否为有效项目
        """
        try:
            project_dir = Path(project_path)
            return (
                project_dir.exists() and
                (project_dir / "project.json").exists()
            )
        except Exception:
            return False

    def get_project_info(self) -> Dict[str, Any]:
        """
        获取当前项目信息

        Returns:
            项目信息字典
        """
        if not self.is_project_loaded or not self.data_manager:
            return {}

        return self.data_manager.get_project_info()

    def create_project_structure(self, project_path: str) -> bool:
        """
        创建标准的项目目录结构

        Args:
            project_path: 项目路径

        Returns:
            创建是否成功
        """
        try:
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)

            # 创建标准目录结构
            directories = [
                "chapters",
                "assets/images",
                "assets/attachments",
                "backups",
                "exports"
            ]

            for dir_name in directories:
                (project_dir / dir_name).mkdir(parents=True, exist_ok=True)

            # 创建README文件
            readme_content = f"""# {project_dir.name}

## 项目结构

- `chapters/` - 章节文件
- `assets/` - 资源文件
  - `images/` - 图片资源
  - `attachments/` - 附件资源
- `backups/` - 自动备份
- `exports/` - 导出文件
- `project.json` - 项目配置
- `roles.json` - 角色数据
- `architecture.md` - 小说架构
- `blueprint.md` - 章节蓝图
- `summary.txt` - 全局概览

## 使用说明

本项目使用InfiniteQuill AI小说生成器创建。

创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            (project_dir / "README.md").write_text(readme_content, encoding='utf-8')

            # 创建默认项目配置
            default_config = {
                "name": project_dir.name,
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "chapters": [],
                "word_count": 0,
                "settings": {
                    "genre": "未分类",
                    "target_chapters": 20,
                    "words_per_chapter": 3000
                }
            }

            config_file = project_dir / "project.json"
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

            logger.info(f"项目结构已创建: {project_path}")
            return True

        except Exception as e:
            logger.error(f"创建项目结构失败: {e}")
            return False

    def get_directory_size(self, path: str) -> int:
        """
        计算目录大小

        Args:
            path: 目录路径

        Returns:
            目录大小（字节）
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception as e:
            logger.error(f"计算目录大小失败: {e}")
            return 0

    def format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 文件大小（字节）

        Returns:
            格式化后的大小字符串
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.2f} {size_names[i]}"

    def get_project_statistics(self) -> Dict[str, Any]:
        """
        获取项目统计信息

        Returns:
            统计信息字典
        """
        if not self.is_project_loaded or not self.data_manager:
            return {}

        try:
            info = self.get_project_info()
            chapter_count = info.get("chapter_count", 0)
            word_count = info.get("word_count", 0)
            role_count = info.get("role_count", 0)

            # 计算项目大小
            project_size = self.get_directory_size(self.project_path)
            chapters_size = self.get_directory_size(
                os.path.join(self.project_path, "chapters")
            )

            # 计算平均章节字数
            avg_words = word_count // chapter_count if chapter_count > 0 else 0

            # 预估完成时间（假设每章3000字，写作速度每小时500字）
            remaining_chapters = max(0, 20 - chapter_count)  # 假设目标是20章
            estimated_hours = (remaining_chapters * 3000) / 500
            estimated_days = estimated_hours / 8  # 每天工作8小时

            return {
                "basic_info": info,
                "statistics": {
                    "chapter_count": chapter_count,
                    "word_count": word_count,
                    "role_count": role_count,
                    "avg_words_per_chapter": avg_words,
                    "project_size": self.format_file_size(project_size),
                    "chapters_size": self.format_file_size(chapters_size)
                },
                "progress": {
                    "completion_rate": min(100, (chapter_count / 20) * 100) if chapter_count > 0 else 0,
                    "estimated_hours_remaining": round(estimated_hours, 1),
                    "estimated_days_remaining": round(estimated_days, 1)
                }
            }

        except Exception as e:
            logger.error(f"获取项目统计失败: {e}")
            return {}

    def auto_save_project(self) -> bool:
        """
        自动保存项目

        Returns:
            保存是否成功
        """
        if not self.is_project_loaded:
            return False

        try:
            # 执行自动保存
            self.save_project()

            # 创建自动备份
            if self.data_manager:
                backup_path = self.data_manager.backup_project()
                logger.debug(f"自动备份已创建: {backup_path}")

            return True

        except Exception as e:
            logger.error(f"自动保存失败: {e}")
            return False

    def rename_project(self, new_name: str) -> bool:
        """
        重命名项目

        Args:
            new_name: 新项目名称

        Returns:
            重命名是否成功
        """
        if not self.is_project_loaded:
            return False

        try:
            # 更新项目配置
            config = self.data_manager.load_project_config()
            config["name"] = new_name
            self.data_manager.save_project_config(config)

            logger.info(f"项目已重命名为: {new_name}")
            return True

        except Exception as e:
            logger.error(f"重命名项目失败: {e}")
            return False

    def export_project(self, export_path: str, format_type: str = "full") -> bool:
        """
        导出项目

        Args:
            export_path: 导出路径
            format_type: 导出格式（full, chapters, summary）

        Returns:
            导出是否成功
        """
        if not self.is_project_loaded:
            return False

        try:
            if format_type == "full":
                # 导出整个项目
                self.data_manager.export_project(export_path)
            elif format_type == "chapters":
                # 只导出章节
                self._export_chapters_only(export_path)
            elif format_type == "summary":
                # 导出项目摘要
                self._export_project_summary(export_path)
            else:
                logger.error(f"不支持的导出格式: {format_type}")
                return False

            logger.info(f"项目已导出到: {export_path}")
            return True

        except Exception as e:
            logger.error(f"导出项目失败: {e}")
            return False

    def _export_chapters_only(self, export_path: str):
        """只导出章节文件"""
        chapters_dir = Path(export_path) / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        for chapter_num in self.data_manager.list_chapters():
            content = self.data_manager.load_chapter(chapter_num)
            chapter_file = chapters_dir / f"chapter_{chapter_num:03d}.md"
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(content)

    def _export_project_summary(self, export_path: str):
        """导出项目摘要"""
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        summary_content = []

        # 项目信息
        info = self.get_project_info()
        summary_content.append(f"# {info.get('name', '未命名项目')}")
        summary_content.append("")
        summary_content.append(f"创建时间: {info.get('created', '')}")
        summary_content.append(f"更新时间: {info.get('updated', '')}")
        summary_content.append("")

        # 统计信息
        stats = self.get_project_statistics()
        if stats:
            summary_content.append("## 统计信息")
            summary_content.append(f"- 章节数量: {stats.get('basic_info', {}).get('chapter_count', 0)}")
            summary_content.append(f"- 总字数: {stats.get('basic_info', {}).get('word_count', 0)}")
            summary_content.append(f"- 角色数量: {stats.get('basic_info', {}).get('role_count', 0)}")
            summary_content.append("")

        # 章节列表
        chapters = self.data_manager.list_chapters()
        if chapters:
            summary_content.append("## 章节列表")
            for ch_num in chapters:
                summary_content.append(f"- 第{ch_num}章")
            summary_content.append("")

        # 保存摘要文件
        summary_file = export_dir / "project_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(summary_content))
