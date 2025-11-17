# coherence_checker.py
# -*- coding: utf-8 -*-
"""
跨章节连贯性验证模块
用于检查多章节小说的情节连续性、角色一致性、设定连贯性等
"""

import re
import json
import logging
import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from llm_adapters import create_llm_adapter
from novel_generator.chapter import load_character_name_registry

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class CoherenceIssue:
    """连贯性问题数据结构"""
    issue_type: str  # 'plot', 'character_name', 'character_trait', 'setting'
    severity: str    # 'high', 'medium', 'low'
    description: str
    location: str    # 章节号和段落位置
    suggestion: str  # 修复建议
    chapters_involved: List[int]  # 涉及的章节号

@dataclass
class CoherenceScore:
    """连贯性分数数据结构"""
    plot_continuity: float  # 情节连续性分数 (0-100)
    character_consistency: float  # 角色一致性分数 (0-100)
    setting_consistency: float  # 设定连贯性分数 (0-100)
    overall_score: float  # 总体分数 (0-100)

@dataclass
class CharacterInfo:
    """角色信息数据结构"""
    name: str
    traits: Dict[str, str]  # 特征字典：性别、年龄、外貌、性格等
    first_appearance: int  # 首次出现的章节号
    appearances: List[int]  # 出现过的章节号

class CoherenceChecker:
    """跨章节连贯性检查器"""

    def __init__(self, llm_config: Dict[str, Any], project_path: Optional[str] = None):
        """
        初始化连贯性检查器

        Args:
            llm_config: LLM配置字典，包含api_key, base_url, model_name等
            project_path: 项目路径，用于加载角色名字注册表
        """
        self.llm_config = llm_config
        # 添加默认timeout参数
        llm_config_with_timeout = {**llm_config, "timeout": llm_config.get("timeout", 600)}
        self.llm_adapter = create_llm_adapter(**llm_config_with_timeout)
        self.issues: List[CoherenceIssue] = []
        self.characters: Dict[str, CharacterInfo] = {}
        self.project_path = project_path

        # 加载角色名字注册表（与Story 3.1集成）
        self.character_name_registry = {}
        if project_path:
            self._load_character_registry()

    def _load_character_registry(self):
        """加载角色名字注册表（与Story 3.1集成）"""
        try:
            registry_file = os.path.join(self.project_path, "character_names.json")
            if os.path.exists(registry_file):
                with open(registry_file, 'r', encoding='utf-8') as f:
                    self.character_name_registry = json.load(f)
                logger.info(f"已加载角色名字注册表，包含 {len(self.character_name_registry)} 个角色")
        except Exception as e:
            logger.error(f"加载角色名字注册表失败: {e}")
            self.character_name_registry = {}

    def check_plot_continuity(self, chapter_n: str, chapter_n_minus_1: str,
                            chapter_n_num: int) -> Tuple[float, List[CoherenceIssue]]:
        """
        检查情节连续性

        Args:
            chapter_n: 第N章内容
            chapter_n_minus_1: 第N-1章内容
            chapter_n_num: 第N章的章节数

        Returns:
            Tuple[分数, 问题列表]
        """
        prompt = f"""请评估以下两个章节的情节连续性:

第{chapter_n_num-1}章摘要:
{self._extract_summary(chapter_n_minus_1)}

第{chapter_n_num}章摘要:
{self._extract_summary(chapter_n)}

评估标准:
1. 情节是否自然延续?(0-100分)
2. 是否有突兀的转折或跳跃?
3. 整体连贯性如何?

请按以下JSON格式回复:
{{
    "score": 85,
    "analysis": "情节自然过渡，没有明显跳跃",
    "issues": [
        {{
            "severity": "medium",
            "description": "第{chapter_n_num}章开头略显突兀",
            "suggestion": "建议增加过渡句，承接上一章结尾"
        }}
    ]
}}"""

        try:
            response = self.llm_adapter.invoke(prompt)
            result = self._parse_json_response(response)

            score = result.get('score', 80)
            issues = []

            for issue_data in result.get('issues', []):
                issue = CoherenceIssue(
                    issue_type='plot',
                    severity=issue_data.get('severity', 'medium'),
                    description=issue_data.get('description', ''),
                    location=f"第{chapter_n_num}章",
                    suggestion=issue_data.get('suggestion', ''),
                    chapters_involved=[chapter_n_num-1, chapter_n_num]
                )
                issues.append(issue)

            return score, issues

        except Exception as e:
            logger.error(f"情节连续性检查失败: {e}")
            return 70.0, [CoherenceIssue(
                issue_type='plot',
                severity='medium',
                description=f"检查失败: {str(e)}",
                location=f"第{chapter_n_num}章",
                suggestion="请手动检查情节连贯性",
                chapters_involved=[chapter_n_num-1, chapter_n_num]
            )]

    def extract_character_names(self, chapter_text: str) -> List[str]:
        """
        提取章节中的角色名字

        Args:
            chapter_text: 章节文本

        Returns:
            角色名字列表
        """
        # 中文人名模式：姓(1-2字)+名(1-2字)
        chinese_name_pattern = r'[\u4e00-\u9fa5]{2,4}(?=[，。！？；：""''（）》《》\\s])'

        # 西式人名模式：首字母大写 + 2-15个字母
        western_name_pattern = r'\b[A-Z][a-z]{1,15}\b(?=[,.!?;:\s"\'()\[\]])'

        # 提取所有可能的名字
        chinese_names = re.findall(chinese_name_pattern, chapter_text)
        western_names = re.findall(western_name_pattern, chapter_text)

        # 过滤常见词汇
        common_words = {'我们', '他们', '她们', '你们', '自己', '大家', '有人', '没人',
                       '这个', '那个', '什么', '怎么', '为什么', '因为', '所以', '但是',
                       'The', 'This', 'That', 'He', 'She', 'It', 'They', 'What', 'When'}

        all_names = []
        for name in chinese_names + western_names:
            if name not in common_words and len(name) >= 2:
                all_names.append(name)

        # 去重并保持顺序
        seen = set()
        unique_names = []
        for name in all_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)

        return unique_names

    def normalize_name(self, name: str) -> str:
        """
        名字标准化处理，处理名字变体

        Args:
            name: 原始名字

        Returns:
            标准化后的名字
        """
        name = name.strip()

        # 处理常见称谓变体
        title_mappings = {
            '先生': '',
            '女士': '',
            '小姐': '',
            '老师': '',
            '医生': '',
            '教授': '',
            'Mr.': '',
            'Mrs.': '',
            'Ms.': '',
            'Dr.': '',
            'Prof.': ''
        }

        for title, replacement in title_mappings.items():
            if name.endswith(title):
                name = name[:-len(title)] + replacement
                break

        # 处理简称变体（如"小李" -> "李明"）
        # 这里简化处理，实际应用中可能需要更复杂的映射
        surname_prefix_mappings = {
            '小': '',
            '老': '',
            '阿': ''
        }

        for prefix, replacement in surname_prefix_mappings.items():
            if name.startswith(prefix) and len(name) == 3:
                # 简单处理：如果是"小李"这样的格式，暂时保留原名
                # 实际应用中可能需要角色注册表来映射
                pass

        return name.strip()

    def check_character_name_consistency(self, chapters: List[str]) -> Tuple[float, List[CoherenceIssue]]:
        """
        检查角色名字一致性（与Story 3.1集成）

        Args:
            chapters: 所有章节内容列表

        Returns:
            Tuple[一致性分数, 问题列表]
        """
        character_appearances = {}  # {角色名: {章节号: [出现次数]}}

        # 收集每章的角色名字
        for i, chapter in enumerate(chapters, 1):
            names = self.extract_character_names(chapter)
            for name in names:
                normalized_name = self.normalize_name(name)
                if normalized_name not in character_appearances:
                    character_appearances[normalized_name] = {}
                if i not in character_appearances[normalized_name]:
                    character_appearances[normalized_name][i] = 0
                character_appearances[normalized_name][i] += 1

        # 检查名字一致性
        issues = []
        total_characters = len(character_appearances)
        consistent_characters = 0

        for character, appearances in character_appearances.items():
            # 如果角色只在单个章节出现，跳过一致性检查
            if len(appearances) < 2:
                consistent_characters += 1
                continue

            # 检查是否有名字变体
            all_names_in_chapters = set()
            for chapter_idx, chapter in enumerate(chapters, 1):
                if chapter_idx in appearances:
                    names_in_chapter = self.extract_character_names(chapter)
                    normalized_names = [self.normalize_name(name) for name in names_in_chapter]
                    all_names_in_chapters.update(normalized_names)

            # 如果存在多个不同的标准化名字，可能存在一致性问题
            if len(all_names_in_chapters) > 1:
                # 检查角色名字注册表是否有相关信息
                registry_info = self._check_character_registry(character, all_names_in_chapters)

                severity = 'medium'
                if registry_info['is_registered']:
                    # 如果是注册表中的角色，问题更严重
                    severity = 'high'
                    description = f"已注册角色'{character}'的名字出现不一致: {', '.join(all_names_in_chapters)}"
                    suggestion = f"应该使用注册表中的名字: {registry_info['registered_name']}"
                else:
                    description = f"角色'{character}'的名字在不同章节中存在变体: {', '.join(all_names_in_chapters)}"
                    suggestion = "建议统一角色名字，或确认是否为不同角色"

                issue = CoherenceIssue(
                    issue_type='character_name',
                    severity=severity,
                    description=description,
                    location=f"第{min(appearances.keys())}-{max(appearances.keys())}章",
                    suggestion=suggestion,
                    chapters_involved=list(appearances.keys())
                )
                issues.append(issue)
            else:
                consistent_characters += 1

        # 检查注册表中的角色是否在文本中正确使用
        registry_issues = self._check_registry_usage(chapters)
        issues.extend(registry_issues)

        # 计算一致性分数
        if total_characters == 0:
            score = 100.0
        else:
            score = (consistent_characters / total_characters) * 100

        return score, issues

    def _check_character_registry(self, character: str, found_names: set) -> Dict[str, Any]:
        """
        检查角色名字注册表中的信息

        Args:
            character: 标准化的角色名
            found_names: 在文本中找到的名字变体

        Returns:
            注册表信息字典
        """
        result = {
            'is_registered': False,
            'registered_name': None,
            'registry_variants': []
        }

        # 检查是否有匹配的注册角色
        for registered_id, registered_name in self.character_name_registry.items():
            # 检查标准化后的名字是否匹配
            if self.normalize_name(registered_name) == character:
                result['is_registered'] = True
                result['registered_name'] = registered_name
                break

        return result

    def _check_registry_usage(self, chapters: List[str]) -> List[CoherenceIssue]:
        """
        检查注册表中的角色名字是否在文本中正确使用

        Args:
            chapters: 所有章节内容列表

        Returns:
            问题列表
        """
        issues = []

        for registered_id, registered_name in self.character_name_registry.items():
            found_in_chapters = []

            # 检查每个章节是否包含该角色
            for i, chapter in enumerate(chapters, 1):
                names_in_chapter = self.extract_character_names(chapter)
                normalized_names = [self.normalize_name(name) for name in names_in_chapter]

                if self.normalize_name(registered_name) in normalized_names:
                    found_in_chapters.append(i)

            # 如果注册角色在多章节中出现，检查名字是否一致
            if len(found_in_chapters) > 1:
                # 检查实际使用的名字是否与注册表一致
                name_variations = set()
                for chapter_idx in found_in_chapters:
                    names_in_chapter = self.extract_character_names(chapters[chapter_idx - 1])
                    for name in names_in_chapter:
                        if self.normalize_name(name) == self.normalize_name(registered_name):
                            name_variations.add(name)

                if len(name_variations) > 1:
                    issue = CoherenceIssue(
                        issue_type='character_name',
                        severity='high',
                        description=f"注册角色'{registered_name}'在文本中有多种写法: {', '.join(name_variations)}",
                        location=f"第{min(found_in_chapters)}-{max(found_in_chapters)}章",
                        suggestion=f"应该统一使用注册表中的名字: {registered_name}",
                        chapters_involved=found_in_chapters
                    )
                    issues.append(issue)

        return issues

    def extract_character_traits(self, chapter_text: str, character_name: str) -> Dict[str, str]:
        """
        从章节文本中提取角色的特征

        Args:
            chapter_text: 章节文本
            character_name: 角色名字

        Returns:
            角色特征字典
        """
        prompt = f"""请从以下文本中提取角色"{character_name}"的特征信息:

文本内容:
{chapter_text[:2000]}  # 限制长度以控制token消耗

请按以下JSON格式回复，如果某项信息未提及请留空:
{{
    "gender": "",
    "age": "",
    "appearance": "",
    "personality": "",
    "occupation": "",
    "background": ""
}}"""

        try:
            response = self.llm_adapter.invoke(prompt)
            result = self._parse_json_response(response)

            # 过滤空值
            traits = {}
            for key, value in result.items():
                if value and value.strip():
                    traits[key] = value.strip()

            return traits

        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return {}

    def check_character_trait_consistency(self, chapters: List[str]) -> Tuple[float, List[CoherenceIssue]]:
        """
        检查角色特征一致性

        Args:
            chapters: 所有章节内容列表

        Returns:
            Tuple[一致性分数, 问题列表]
        """
        # 首先收集所有角色名字
        all_characters = set()
        for chapter in chapters:
            names = self.extract_character_names(chapter)
            all_characters.update([self.normalize_name(name) for name in names])

        issues = []
        character_consistency_scores = []

        for character in all_characters:
            character_traits = {}  # {章节号: 特征字典}

            # 提取每章中的角色特征
            for i, chapter in enumerate(chapters, 1):
                if character in [self.normalize_name(name) for name in self.extract_character_names(chapter)]:
                    traits = self.extract_character_traits(chapter, character)
                    if traits:  # 只保存有特征的章节
                        character_traits[i] = traits

            # 如果角色在多章节中有特征描述，检查一致性
            if len(character_traits) > 1:
                consistency_score = self._evaluate_trait_consistency(character, character_traits)
                character_consistency_scores.append(consistency_score)

                if consistency_score < 80:  # 一致性阈值
                    # 生成具体的不一致问题
                    inconsistency_details = self._find_trait_inconsistencies(character, character_traits)
                    for detail in inconsistency_details:
                        issue = CoherenceIssue(
                            issue_type='character_trait',
                            severity='high' if consistency_score < 60 else 'medium',
                            description=detail['description'],
                            location=detail['location'],
                            suggestion=detail['suggestion'],
                            chapters_involved=list(character_traits.keys())
                        )
                        issues.append(issue)

        # 计算总体角色一致性分数
        if character_consistency_scores:
            avg_score = sum(character_consistency_scores) / len(character_consistency_scores)
        else:
            avg_score = 100.0  # 没有需要检查的角色

        return avg_score, issues

    def extract_story_setting(self, chapter_text: str) -> Dict[str, str]:
        """
        提取故事设定信息

        Args:
            chapter_text: 章节文本

        Returns:
            设定信息字典
        """
        prompt = f"""请从以下章节中提取故事设定信息:

章节内容:
{chapter_text[:2000]}

请按以下JSON格式回复，如果某项信息未提及请留空:
{{
    "time_period": "",
    "world_type": "",
    "location": "",
    "technology_level": "",
    "social_structure": ""
}}"""

        try:
            response = self.llm_adapter.invoke(prompt)
            result = self._parse_json_response(response)

            # 过滤空值
            setting = {}
            for key, value in result.items():
                if value and value.strip():
                    setting[key] = value.strip()

            return setting

        except Exception as e:
            logger.error(f"设定提取失败: {e}")
            return {}

    def check_setting_consistency(self, chapters: List[str]) -> Tuple[float, List[CoherenceIssue]]:
        """
        检查故事设定连贯性

        Args:
            chapters: 所有章节内容列表

        Returns:
            Tuple[连贯性分数, 问题列表]
        """
        settings = {}  # {章节号: 设定字典}

        # 提取每章的设定信息
        for i, chapter in enumerate(chapters, 1):
            setting = self.extract_story_setting(chapter)
            if setting:  # 只保存有设定信息的章节
                settings[i] = setting

        issues = []
        consistency_scores = []

        # 检查各个设定维度的一致性
        setting_dimensions = ['time_period', 'world_type', 'location', 'technology_level', 'social_structure']

        for dimension in setting_dimensions:
            dimension_values = {}  # {值: [章节号列表]}

            for chapter_num, setting in settings.items():
                if dimension in setting and setting[dimension]:
                    value = setting[dimension]
                    if value not in dimension_values:
                        dimension_values[value] = []
                    dimension_values[value].append(chapter_num)

            # 如果某个维度有多种不同的值，可能存在不一致
            if len(dimension_values) > 1:
                # 使用LLM评估这些差异是否合理
                values_text = '\n'.join([f"- {v}: 第{', '.join(map(str, chapters))}章"
                                       for v, chapters in dimension_values.items()])

                prompt = f"""以下设定维度在不同章节中有不同的描述:

设定维度: {dimension}
不同描述:
{values_text}

请判断这些差异是否合理或不一致，按JSON格式回复:
{{
    "is_consistent": true/false,
    "score": 85,
    "analysis": "分析说明",
    "issues": ["问题描述1", "问题描述2"]
}}"""

                try:
                    response = self.llm_adapter.invoke(prompt)
                    result = self._parse_json_response(response)

                    if not result.get('is_consistent', True):
                        score = result.get('score', 70)
                        consistency_scores.append(score)

                        for issue_desc in result.get('issues', []):
                            issue = CoherenceIssue(
                                issue_type='setting',
                                severity='medium',
                                description=f"设定'{dimension}'不一致: {issue_desc}",
                                location=f"第{min([ch for vals in dimension_values.values() for ch in vals])}-{max([ch for vals in dimension_values.values() for ch in vals])}章",
                                suggestion="建议统一设定描述，或提供合理的解释",
                                chapters_involved=list(settings.keys())
                            )
                            issues.append(issue)
                    else:
                        consistency_scores.append(95)  # 认为一致

                except Exception as e:
                    logger.error(f"设定一致性评估失败: {e}")
                    consistency_scores.append(75)

        # 计算总体设定一致性分数
        if consistency_scores:
            avg_score = sum(consistency_scores) / len(consistency_scores)
        else:
            avg_score = 100.0  # 没有需要检查的设定

        return avg_score, issues

    def calculate_overall_scores(self, plot_score: float, character_score: float, setting_score: float) -> CoherenceScore:
        """
        计算总体连贯性分数

        Args:
            plot_score: 情节连贯性分数
            character_score: 角色一致性分数
            setting_score: 设定连贯性分数

        Returns:
            完整的连贯性分数对象
        """
        # 加权平均 (参考Dev Notes中的权重)
        overall_score = (plot_score * 0.4 + character_score * 0.3 + setting_score * 0.3)

        return CoherenceScore(
            plot_continuity=plot_score,
            character_consistency=character_score,
            setting_consistency=setting_score,
            overall_score=overall_score
        )

    def generate_quality_report(self, scores: CoherenceScore, issues: List[CoherenceIssue]) -> str:
        """
        生成质量报告

        Args:
            scores: 连贯性分数
            issues: 问题列表

        Returns:
            格式化的质量报告文本
        """
        report = f"""# 小说连贯性检查报告

**总体质量分数: {scores.overall_score:.1f}/100**

## 情节连贯度: {scores.plot_continuity:.1f}/100 {'✅' if scores.plot_continuity >= 80 else '⚠️' if scores.plot_continuity >= 60 else '❌'}
"""

        # 按类型分组问题
        plot_issues = [issue for issue in issues if issue.issue_type == 'plot']
        character_name_issues = [issue for issue in issues if issue.issue_type == 'character_name']
        character_trait_issues = [issue for issue in issues if issue.issue_type == 'character_trait']
        setting_issues = [issue for issue in issues if issue.issue_type == 'setting']

        # 情节问题详情
        if plot_issues:
            report += f"\n**发现{len(plot_issues)}个情节问题**:\n"
            for issue in plot_issues:
                report += f"- {issue.description} (第{', '.join(map(str, issue.chapters_involved))}章)\n"
                report += f"  建议: {issue.suggestion}\n"
        else:
            report += "- 未发现明显情节连贯性问题\n"

        # 角色一致性详情
        report += f"\n## 角色一致性: {scores.character_consistency:.1f}/100 {'✅' if scores.character_consistency >= 80 else '⚠️' if scores.character_consistency >= 60 else '❌'}\n"

        total_character_issues = len(character_name_issues) + len(character_trait_issues)
        if total_character_issues > 0:
            report += f"**发现{total_character_issues}个角色问题**:\n"

            for issue in character_name_issues:
                report += f"- 角色名字不一致: {issue.description}\n"
                report += f"  位置: {issue.location}\n"
                report += f"  建议: {issue.suggestion}\n"

            for issue in character_trait_issues:
                severity_icon = "🔴" if issue.severity == 'high' else "🟡"
                report += f"- {severity_icon} 角色特征不一致: {issue.description}\n"
                report += f"  位置: {issue.location}\n"
                report += f"  建议: {issue.suggestion}\n"
        else:
            report += "- 角色名字和特征保持一致\n"

        # 设定连贯性详情
        report += f"\n## 设定连贯度: {scores.setting_consistency:.1f}/100 {'✅' if scores.setting_consistency >= 80 else '⚠️' if scores.setting_consistency >= 60 else '❌'}\n"

        if setting_issues:
            report += f"**发现{len(setting_issues)}个设定问题**:\n"
            for issue in setting_issues:
                report += f"- {issue.description}\n"
                report += f"  位置: {issue.location}\n"
                report += f"  建议: {issue.suggestion}\n"
        else:
            report += "- 故事设定保持一致\n"

        # 总体建议
        report += "\n## 建议\n"
        if issues:
            high_priority_issues = [issue for issue in issues if issue.severity == 'high']
            if high_priority_issues:
                report += "### 高优先级问题\n"
                for issue in high_priority_issues:
                    report += f"1. {issue.description}\n"
                    report += f"   建议: {issue.suggestion}\n"

            report += "\n### 改进建议\n"
            report += "1. 重点关注角色特征的合理演进\n"
            report += "2. 确保情节过渡的自然性\n"
            report += "3. 维护故事设定的统一性\n"
        else:
            report += "🎉 小说连贯性良好，未发现重大问题！\n"

        return report

    def run_coherence_check(self, chapters: List[str]) -> Tuple[CoherenceScore, List[CoherenceIssue], str]:
        """
        运行完整的连贯性检查

        Args:
            chapters: 所有章节内容列表

        Returns:
            Tuple[分数对象, 问题列表, 质量报告]
        """
        logger.info(f"开始对{len(chapters)}个章节进行连贯性检查")

        all_issues = []

        # 1. 检查情节连续性
        plot_scores = []
        for i in range(1, len(chapters)):
            score, issues = self.check_plot_continuity(chapters[i], chapters[i-1], i+1)
            plot_scores.append(score)
            all_issues.extend(issues)

        avg_plot_score = sum(plot_scores) / len(plot_scores) if plot_scores else 100.0

        # 2. 检查角色名字一致性
        character_name_score, name_issues = self.check_character_name_consistency(chapters)
        all_issues.extend(name_issues)

        # 3. 检查角色特征一致性
        character_trait_score, trait_issues = self.check_character_trait_consistency(chapters)
        all_issues.extend(trait_issues)

        # 合并角色一致性分数
        overall_character_score = (character_name_score + character_trait_score) / 2

        # 4. 检查设定连贯性
        setting_score, setting_issues = self.check_setting_consistency(chapters)
        all_issues.extend(setting_issues)

        # 5. 计算总体分数
        scores = self.calculate_overall_scores(avg_plot_score, overall_character_score, setting_score)

        # 6. 生成质量报告
        report = self.generate_quality_report(scores, all_issues)

        logger.info(f"连贯性检查完成 - 总体分数: {scores.overall_score:.1f}, 发现问题: {len(all_issues)}个")

        return scores, all_issues, report

    # ============== 辅助方法 ==============

    def _extract_summary(self, chapter_text: str) -> str:
        """提取章节摘要"""
        # 简单实现：取前500字符作为摘要
        # 实际应用中可以使用更复杂的摘要提取算法
        return chapter_text[:500] + "..." if len(chapter_text) > 500 else chapter_text

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析LLM的JSON响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # 如果都失败了，返回默认结构
            logger.warning(f"无法解析JSON响应: {response}")
            return {}

    def _evaluate_trait_consistency(self, character: str, traits_by_chapter: Dict[int, Dict[str, str]]) -> float:
        """评估角色特征一致性"""
        if len(traits_by_chapter) < 2:
            return 100.0

        # 构建检查提示
        traits_text = []
        for chapter_num, traits in traits_by_chapter.items():
            traits_str = ', '.join([f"{k}: {v}" for k, v in traits.items()])
            traits_text.append(f"第{chapter_num}章: {traits_str}")

        prompt = f"""请评估角色"{character}"在不同章节中的特征一致性:

{chr(10).join(traits_text)}

请评估特征是否一致或合理演进，按JSON格式回复:
{{
    "score": 85,
    "analysis": "特征描述基本一致，年龄变化合理"
}}"""

        try:
            response = self.llm_adapter.invoke(prompt)
            result = self._parse_json_response(response)
            return float(result.get('score', 75))
        except Exception as e:
            logger.error(f"特征一致性评估失败: {e}")
            return 70.0

    def _find_trait_inconsistencies(self, character: str, traits_by_chapter: Dict[int, Dict[str, str]]) -> List[Dict[str, str]]:
        """找到具体的特征不一致问题"""
        inconsistencies = []

        # 收集所有特征维度
        all_traits = set()
        for traits in traits_by_chapter.values():
            all_traits.update(traits.keys())

        # 检查每个维度的不一致
        for trait in all_traits:
            values_by_chapter = {}
            for chapter_num, traits in traits_by_chapter.items():
                if trait in traits:
                    value = traits[trait]
                    if value not in values_by_chapter:
                        values_by_chapter[value] = []
                    values_by_chapter[value].append(chapter_num)

            # 如果同一个特征有不同的值，可能存在不一致
            if len(values_by_chapter) > 1:
                chapters_list = [ch for vals in values_by_chapter.values() for ch in vals]
                inconsistencies.append({
                    'description': f"角色'{character}'的{trait}在不同章节中描述不一致",
                    'location': f"第{min(chapters_list)}-{max(chapters_list)}章",
                    'suggestion': f"建议检查{trait}的一致性，确保变化合理或有明确的情节支撑"
                })

        return inconsistencies

# ============== 便捷函数 ==============

def run_coherence_check(novel_project_path: str, chapters: List[str], llm_config: Dict[str, Any]) -> Tuple[CoherenceScore, List[CoherenceIssue], str]:
    """
    运行连贯性检查的便捷函数

    Args:
        novel_project_path: 小说项目路径
        chapters: 章节内容列表
        llm_config: LLM配置

    Returns:
        Tuple[分数对象, 问题列表, 质量报告]
    """
    checker = CoherenceChecker(llm_config)
    return checker.run_coherence_check(chapters)