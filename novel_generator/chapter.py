# novel_generator/chapter.py
# -*- coding: utf-8 -*-
"""
章节草稿生成及获取历史章节文本、当前章节摘要等
"""
import os
import json
import logging
import re  # 添加re模块导入
from llm_adapters import create_llm_adapter
from prompt_definitions import (
    first_chapter_draft_prompt, 
    next_chapter_draft_prompt, 
    summarize_recent_chapters_prompt,
    knowledge_filter_prompt,
    knowledge_search_prompt
)
from novel_generator.chapter_directory_parser import get_chapter_info_from_blueprint
from novel_generator.common import invoke_with_cleaning
from utils import read_file, clear_file_content, save_string_to_txt
from novel_generator.vectorstore_utils import (
    get_relevant_context_from_vector_store,
    load_vector_store  # 添加导入
)
logging.basicConfig(
    filename='app.log',      # 日志文件名
    filemode='a',            # 追加模式（'w' 会覆盖）
    level=logging.INFO,      # 记录 INFO 及以上级别的日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_last_n_chapters_text(chapters_dir: str, current_chapter_num: int, n: int = 3) -> list:
    """
    从目录 chapters_dir 中获取最近 n 章的文本内容，返回文本列表。
    """
    texts = []
    start_chap = max(1, current_chapter_num - n)
    for c in range(start_chap, current_chapter_num):
        chap_file = os.path.join(chapters_dir, f"chapter_{c}.txt")
        if os.path.exists(chap_file):
            text = read_file(chap_file).strip()
            texts.append(text)
        else:
            texts.append("")
    return texts

def summarize_recent_chapters(
    interface_format: str,
    api_key: str,
    base_url: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
    chapters_text_list: list,
    novel_number: int,            # 新增参数
    chapter_info: dict,           # 新增参数
    next_chapter_info: dict,      # 新增参数
    timeout: int = 600
) -> str:  # 修改返回值类型为 str，不再是 tuple
    """
    根据前三章内容生成当前章节的精准摘要。
    如果解析失败，则返回空字符串。
    """
    try:
        combined_text = "\n".join(chapters_text_list).strip()
        if not combined_text:
            return ""
            
        # 限制组合文本长度
        max_combined_length = 4000
        if len(combined_text) > max_combined_length:
            combined_text = combined_text[-max_combined_length:]
            
        llm_adapter = create_llm_adapter(
            interface_format=interface_format,
            base_url=base_url,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        # 确保所有参数都有默认值
        chapter_info = chapter_info or {}
        next_chapter_info = next_chapter_info or {}
        
        prompt = summarize_recent_chapters_prompt.format(
            combined_text=combined_text,
            novel_number=novel_number,
            chapter_title=chapter_info.get("chapter_title", "未命名"),
            chapter_role=chapter_info.get("chapter_role", "常规章节"),
            chapter_purpose=chapter_info.get("chapter_purpose", "内容推进"),
            suspense_level=chapter_info.get("suspense_level", "中等"),
            foreshadowing=chapter_info.get("foreshadowing", "无"),
            plot_twist_level=chapter_info.get("plot_twist_level", "★☆☆☆☆"),
            chapter_summary=chapter_info.get("chapter_summary", ""),
            next_chapter_number=novel_number + 1,
            next_chapter_title=next_chapter_info.get("chapter_title", "（未命名）"),
            next_chapter_role=next_chapter_info.get("chapter_role", "过渡章节"),
            next_chapter_purpose=next_chapter_info.get("chapter_purpose", "承上启下"),
            next_chapter_summary=next_chapter_info.get("chapter_summary", "衔接过渡内容"),
            next_chapter_suspense_level=next_chapter_info.get("suspense_level", "中等"),
            next_chapter_foreshadowing=next_chapter_info.get("foreshadowing", "无特殊伏笔"),
            next_chapter_plot_twist_level=next_chapter_info.get("plot_twist_level", "★☆☆☆☆")
        )
        
        response_text = invoke_with_cleaning(llm_adapter, prompt)
        summary = extract_summary_from_response(response_text)
        
        if not summary:
            logging.warning("Failed to extract summary, using full response")
            return response_text[:2000]  # 限制长度
            
        return summary[:2000]  # 限制摘要长度
        
    except Exception as e:
        logging.error(f"Error in summarize_recent_chapters: {str(e)}")
        return ""

def extract_summary_from_response(response_text: str) -> str:
    """从响应文本中提取摘要部分"""
    if not response_text:
        return ""
        
    # 查找摘要标记
    summary_markers = [
        "当前章节摘要:", 
        "章节摘要:",
        "摘要:",
        "本章摘要:"
    ]
    
    for marker in summary_markers:
        if (marker in response_text):
            parts = response_text.split(marker, 1)
            if len(parts) > 1:
                return parts[1].strip()
    
    return response_text.strip()

def format_chapter_info(chapter_info: dict) -> str:
    """将章节信息字典格式化为文本"""
    template = """
章节编号：第{number}章
章节标题：《{title}》
章节定位：{role}
核心作用：{purpose}
主要人物：{characters}
关键道具：{items}
场景地点：{location}
伏笔设计：{foreshadow}
悬念密度：{suspense}
转折程度：{twist}
章节简述：{summary}
"""
    return template.format(
        number=chapter_info.get('chapter_number', '未知'),
        title=chapter_info.get('chapter_title', '未知'),
        role=chapter_info.get('chapter_role', '未知'),
        purpose=chapter_info.get('chapter_purpose', '未知'),
        characters=chapter_info.get('characters_involved', '未指定'),
        items=chapter_info.get('key_items', '未指定'),
        location=chapter_info.get('scene_location', '未指定'),
        foreshadow=chapter_info.get('foreshadowing', '无'),
        suspense=chapter_info.get('suspense_level', '一般'),
        twist=chapter_info.get('plot_twist_level', '★☆☆☆☆'),
        summary=chapter_info.get('chapter_summary', '未提供')
    )

def parse_search_keywords(response_text: str) -> list:
    """解析新版关键词格式（示例输入：'科技公司·数据泄露\n地下实验室·基因编辑'）"""
    return [
        line.strip().replace('·', ' ')
        for line in response_text.strip().split('\n')
        if '·' in line
    ][:5]  # 最多取5组

def apply_content_rules(texts: list, novel_number: int) -> list:
    """应用内容处理规则"""
    processed = []
    for text in texts:
        if re.search(r'第[\d]+章', text) or re.search(r'chapter_[\d]+', text):
            chap_nums = list(map(int, re.findall(r'\d+', text)))
            recent_chap = max(chap_nums) if chap_nums else 0
            time_distance = novel_number - recent_chap
            
            if time_distance <= 2:
                processed.append(f"[SKIP] 跳过近章内容：{text[:120]}...")
            elif 3 <= time_distance <= 5:
                processed.append(f"[MOD40%] {text}（需修改≥40%）")
            else:
                processed.append(f"[OK] {text}（可引用核心）")
        else:
            processed.append(f"[PRIOR] {text}（优先使用）")
    return processed

def apply_knowledge_rules(contexts: list, chapter_num: int) -> list:
    """应用知识库使用规则"""
    processed = []
    for text in contexts:
        # 检测历史章节内容
        if "第" in text and "章" in text:
            # 提取章节号判断时间远近
            chap_nums = [int(s) for s in text.split() if s.isdigit()]
            recent_chap = max(chap_nums) if chap_nums else 0
            time_distance = chapter_num - recent_chap
            
            # 相似度处理规则
            if time_distance <= 3:  # 近三章内容
                processed.append(f"[历史章节限制] 跳过近期内容: {text[:50]}...")
                continue
                
            # 允许引用但需要转换
            processed.append(f"[历史参考] {text} (需进行30%以上改写)")
        else:
            # 第三方知识优先处理
            processed.append(f"[外部知识] {text}")
    return processed

def get_filtered_knowledge_context(
    api_key: str,
    base_url: str,
    model_name: str,
    interface_format: str,
    embedding_adapter,
    filepath: str,
    chapter_info: dict,
    retrieved_texts: list,
    max_tokens: int = 2048,
    timeout: int = 600
) -> str:
    """优化后的知识过滤处理"""
    if not retrieved_texts:
        return "（无相关知识库内容）"

    try:
        processed_texts = apply_knowledge_rules(retrieved_texts, chapter_info.get('chapter_number', 0))
        llm_adapter = create_llm_adapter(
            interface_format=interface_format,
            base_url=base_url,
            model_name=model_name,
            api_key=api_key,
            temperature=0.3,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        # 限制检索文本长度并格式化
        formatted_texts = []
        max_text_length = 600
        for i, text in enumerate(processed_texts, 1):
            if len(text) > max_text_length:
                text = text[:max_text_length] + "..."
            formatted_texts.append(f"[预处理结果{i}]\n{text}")

        # 使用格式化函数处理章节信息
        formatted_chapter_info = (
            f"当前章节定位：{chapter_info.get('chapter_role', '')}\n"
            f"核心目标：{chapter_info.get('chapter_purpose', '')}\n"
            f"关键要素：{chapter_info.get('characters_involved', '')} | "
            f"{chapter_info.get('key_items', '')} | "
            f"{chapter_info.get('scene_location', '')}"
        )

        prompt = knowledge_filter_prompt.format(
            chapter_info=formatted_chapter_info,
            retrieved_texts="\n\n".join(formatted_texts) if formatted_texts else "（无检索结果）"
        )
        
        filtered_content = invoke_with_cleaning(llm_adapter, prompt)
        return filtered_content if filtered_content else "（知识内容过滤失败）"
        
    except Exception as e:
        logging.error(f"Error in knowledge filtering: {str(e)}")
        return "（内容过滤过程出错）"

def build_chapter_prompt(
    api_key: str,
    base_url: str,
    model_name: str,
    filepath: str,
    novel_number: int,
    word_number: int,
    temperature: float,
    user_guidance: str,
    characters_involved: str,
    key_items: str,
    scene_location: str,
    time_constraint: str,
    embedding_api_key: str,
    embedding_url: str,
    embedding_interface_format: str,
    embedding_model_name: str,
    embedding_retrieval_k: int = 2,
    interface_format: str = "openai",
    max_tokens: int = 2048,
    timeout: int = 600
) -> str:
    """
    构造当前章节的请求提示词（完整实现版）
    修改重点：
    1. 优化知识库检索流程
    2. 新增内容重复检测机制
    3. 集成提示词应用规则
    """
    # 读取基础文件
    arch_file = os.path.join(filepath, "Novel_architecture.txt")
    novel_architecture_text = read_file(arch_file)
    directory_file = os.path.join(filepath, "Novel_directory.txt")
    blueprint_text = read_file(directory_file)
    global_summary_file = os.path.join(filepath, "global_summary.txt")
    global_summary_text = read_file(global_summary_file)
    character_state_file = os.path.join(filepath, "character_state.txt")
    character_state_text = read_file(character_state_file)
    
    # 获取章节信息
    chapter_info = get_chapter_info_from_blueprint(blueprint_text, novel_number)
    chapter_title = chapter_info["chapter_title"]
    chapter_role = chapter_info["chapter_role"]
    chapter_purpose = chapter_info["chapter_purpose"]
    suspense_level = chapter_info["suspense_level"]
    foreshadowing = chapter_info["foreshadowing"]
    plot_twist_level = chapter_info["plot_twist_level"]
    chapter_summary = chapter_info["chapter_summary"]

    # 获取下一章节信息
    next_chapter_number = novel_number + 1
    next_chapter_info = get_chapter_info_from_blueprint(blueprint_text, next_chapter_number)
    next_chapter_title = next_chapter_info.get("chapter_title", "（未命名）")
    next_chapter_role = next_chapter_info.get("chapter_role", "过渡章节")
    next_chapter_purpose = next_chapter_info.get("chapter_purpose", "承上启下")
    next_chapter_suspense = next_chapter_info.get("suspense_level", "中等")
    next_chapter_foreshadow = next_chapter_info.get("foreshadowing", "无特殊伏笔")
    next_chapter_twist = next_chapter_info.get("plot_twist_level", "★☆☆☆☆")
    next_chapter_summary = next_chapter_info.get("chapter_summary", "衔接过渡内容")

    # 创建章节目录
    chapters_dir = os.path.join(filepath, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)

    # 第一章特殊处理
    if novel_number == 1:
        return first_chapter_draft_prompt.format(
            novel_number=novel_number,
            word_number=word_number,
            chapter_title=chapter_title,
            chapter_role=chapter_role,
            chapter_purpose=chapter_purpose,
            suspense_level=suspense_level,
            foreshadowing=foreshadowing,
            plot_twist_level=plot_twist_level,
            chapter_summary=chapter_summary,
            characters_involved=characters_involved,
            key_items=key_items,
            scene_location=scene_location,
            time_constraint=time_constraint,
            user_guidance=user_guidance,
            novel_setting=novel_architecture_text
        )

    # 获取前文内容和摘要
    recent_texts = get_last_n_chapters_text(chapters_dir, novel_number, n=3)

    # 新增：基于向量检索的上下文检索
    context_from_previous_chapter = ""
    context_stats = {}
    try:
        from .context_retriever import retrieve_context, generate_project_id

        # 创建嵌入适配器
        embedding_adapter = create_embedding_adapter(
            embedding_interface_format,
            embedding_api_key,
            embedding_url,
            embedding_model_name
        )

        # 生成项目ID
        project_id = generate_project_id(filepath)

        # 构建查询（使用章节蓝图信息）
        context_query = f"""
        章节标题: {chapter_title}
        章节角色: {characters_involved}
        场景地点: {scene_location}
        章节作用: {chapter_purpose}
        情节预告: {foreshadowing}
        """

        # 检索前一章上下文
        context_from_previous_chapter, context_stats = retrieve_context(
            embedding_adapter=embedding_adapter,
            query=context_query.strip(),
            filepath=filepath,
            chapter_num=int(novel_number),
            project_id=project_id,
            max_context_tokens=2000,
            k=3
        )

        logging.info(f"Context retrieval result: {context_stats}")

    except Exception as e:
        logging.error(f"Error in context retrieval: {str(e)}")
        context_from_previous_chapter = ""
        context_stats = {"retrieved": False, "reason": "error"}

    try:
        logging.info("Attempting to generate summary")
        short_summary = summarize_recent_chapters(
            interface_format=interface_format,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            chapters_text_list=recent_texts,
            novel_number=novel_number,
            chapter_info=chapter_info,
            next_chapter_info=next_chapter_info,
            timeout=timeout
        )
        logging.info("Summary generated successfully")
    except Exception as e:
        logging.error(f"Error in summarize_recent_chapters: {str(e)}")
        short_summary = "（摘要生成失败）"

    # 获取前一章结尾
    previous_excerpt = ""
    for text in reversed(recent_texts):
        if text.strip():
            previous_excerpt = text[-800:] if len(text) > 800 else text
            break

    # 知识库检索和处理
    try:
        # 生成检索关键词
        llm_adapter = create_llm_adapter(
            interface_format=interface_format,
            base_url=base_url,
            model_name=model_name,
            api_key=api_key,
            temperature=0.3,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        search_prompt = knowledge_search_prompt.format(
            chapter_number=novel_number,
            chapter_title=chapter_title,
            characters_involved=characters_involved,
            key_items=key_items,
            scene_location=scene_location,
            chapter_role=chapter_role,
            chapter_purpose=chapter_purpose,
            foreshadowing=foreshadowing,
            short_summary=short_summary,
            user_guidance=user_guidance,
            time_constraint=time_constraint
        )
        
        search_response = invoke_with_cleaning(llm_adapter, search_prompt)
        keyword_groups = parse_search_keywords(search_response)

        # 执行向量检索
        all_contexts = []
        from embedding_adapters import create_embedding_adapter
        embedding_adapter = create_embedding_adapter(
            embedding_interface_format,
            embedding_api_key,
            embedding_url,
            embedding_model_name
        )
        
        store = load_vector_store(embedding_adapter, filepath)
        if store:
            collection_size = store._collection.count()
            actual_k = min(embedding_retrieval_k, max(1, collection_size))
            
            for group in keyword_groups:
                context = get_relevant_context_from_vector_store(
                    embedding_adapter=embedding_adapter,
                    query=group,
                    filepath=filepath,
                    k=actual_k
                )
                if context:
                    if any(kw in group.lower() for kw in ["技法", "手法", "模板"]):
                        all_contexts.append(f"[TECHNIQUE] {context}")
                    elif any(kw in group.lower() for kw in ["设定", "技术", "世界观"]):
                        all_contexts.append(f"[SETTING] {context}")
                    else:
                        all_contexts.append(f"[GENERAL] {context}")

        # 应用内容规则
        processed_contexts = apply_content_rules(all_contexts, novel_number)
        
        # 执行知识过滤
        chapter_info_for_filter = {
            "chapter_number": novel_number,
            "chapter_title": chapter_title,
            "chapter_role": chapter_role,
            "chapter_purpose": chapter_purpose,
            "characters_involved": characters_involved,
            "key_items": key_items,
            "scene_location": scene_location,
            "foreshadowing": foreshadowing,  # 修复拼写错误
            "suspense_level": suspense_level,
            "plot_twist_level": plot_twist_level,
            "chapter_summary": chapter_summary,
            "time_constraint": time_constraint
        }
        
        filtered_context = get_filtered_knowledge_context(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            interface_format=interface_format,
            embedding_adapter=embedding_adapter,
            filepath=filepath,
            chapter_info=chapter_info_for_filter,
            retrieved_texts=processed_contexts,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
    except Exception as e:
        logging.error(f"知识处理流程异常：{str(e)}")
        filtered_context = "（知识库处理失败）"

    # 返回最终提示词
    return next_chapter_draft_prompt.format(
        user_guidance=user_guidance if user_guidance else "无特殊指导",
        global_summary=global_summary_text,
        previous_chapter_excerpt=previous_excerpt,
        character_state=character_state_text,
        short_summary=short_summary,
        novel_number=novel_number,
        chapter_title=chapter_title,
        chapter_role=chapter_role,
        chapter_purpose=chapter_purpose,
        suspense_level=suspense_level,
        foreshadowing=foreshadowing,
        plot_twist_level=plot_twist_level,
        chapter_summary=chapter_summary,
        word_number=word_number,
        characters_involved=characters_involved,
        key_items=key_items,
        scene_location=scene_location,
        time_constraint=time_constraint,
        next_chapter_number=next_chapter_number,
        next_chapter_title=next_chapter_title,
        next_chapter_role=next_chapter_role,
        next_chapter_purpose=next_chapter_purpose,
        next_chapter_suspense_level=next_chapter_suspense,
        next_chapter_foreshadowing=next_chapter_foreshadow,
        next_chapter_plot_twist_level=next_chapter_twist,
        next_chapter_summary=next_chapter_summary,
        context_from_previous_chapter=context_from_previous_chapter,
        filtered_context=filtered_context
    )

def generate_chapter_draft(
    api_key: str,
    base_url: str,
    model_name: str, 
    filepath: str,
    novel_number: int,
    word_number: int,
    temperature: float,
    user_guidance: str,
    characters_involved: str,
    key_items: str,
    scene_location: str,
    time_constraint: str,
    embedding_api_key: str,
    embedding_url: str,
    embedding_interface_format: str,
    embedding_model_name: str,
    embedding_retrieval_k: int = 2,
    interface_format: str = "openai",
    max_tokens: int = 2048,
    timeout: int = 600,
    custom_prompt_text: str = None
) -> str:
    """
    生成章节草稿，支持自定义提示词
    """
    if custom_prompt_text is None:
        prompt_text = build_chapter_prompt(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            filepath=filepath,
            novel_number=novel_number,
            word_number=word_number,
            temperature=temperature,
            user_guidance=user_guidance,
            characters_involved=characters_involved,
            key_items=key_items,
            scene_location=scene_location,
            time_constraint=time_constraint,
            embedding_api_key=embedding_api_key,
            embedding_url=embedding_url,
            embedding_interface_format=embedding_interface_format,
            embedding_model_name=embedding_model_name,
            embedding_retrieval_k=embedding_retrieval_k,
            interface_format=interface_format,
            max_tokens=max_tokens,
            timeout=timeout
        )
    else:
        prompt_text = custom_prompt_text

    chapters_dir = os.path.join(filepath, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)

    llm_adapter = create_llm_adapter(
        interface_format=interface_format,
        base_url=base_url,
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout
    )

    chapter_content = invoke_with_cleaning(llm_adapter, prompt_text)
    if not chapter_content.strip():
        logging.warning("Generated chapter draft is empty.")
    chapter_file = os.path.join(chapters_dir, f"chapter_{novel_number}.txt")
    clear_file_content(chapter_file)
    save_string_to_txt(chapter_content, chapter_file)
    logging.info(f"[Draft] Chapter {novel_number} generated as a draft.")
    return chapter_content

# =============== 角色名字验证和管理功能 ===============

def validate_character_name(name: str, expected_traits: dict = None) -> tuple[bool, str]:
    """
    验证角色名字是否符合合理性要求

    Args:
        name: 待验证的名字
        expected_traits: 期望的角色特征，包含gender等

    Returns:
        (是否有效, 错误信息)
    """
    if not name or not isinstance(name, str):
        return False, "名字不能为空"

    # 去除前后空格
    name = name.strip()

    # 1. 长度验证
    if len(name) < 2 or len(name) > 4:
        return False, f"名字长度必须在2-4个字符之间，当前长度：{len(name)}"

    # 2. 字符有效性检查 - 只允许中文字符
    if not re.match(r'^[\u4e00-\u9fa5]+$', name):
        return False, "名字只能包含中文字符，不能包含数字、特殊符号或英文字母"

    # 3. 乱码检测
    try:
        name.encode('utf-8').decode('utf-8')
    except UnicodeError:
        return False, "名字包含无效的Unicode字符"

    # 4. 性别一致性检查
    if expected_traits and 'gender' in expected_traits:
        gender = expected_traits['gender']
        if gender == '男':
            female_chars = ['娜', '丽', '婉', '婷', '芳', '蓉', '秀', '慧', '珍', '萍', '莉', '霞', '燕']
            if any(char in name for char in female_chars):
                return False, f"男性角色名字不应包含女性化字词：{name}"
        elif gender == '女':
            male_chars = ['刚', '强', '勇', '猛', '霸', '威', '烈', '悍', '彪', '雄', '豪', '峻', '峰']
            if any(char in name for char in male_chars):
                return False, f"女性角色名字不应包含男性化字词：{name}"

    # 5. 文化背景合理性 - 检查是否为常见中文姓氏
    common_surnames = ['李', '王', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
    if len(name) >= 2:
        first_char = name[0]
        if first_char not in common_surnames:
            logging.warning(f"名字 '{name}' 的姓氏不常见，但仍在接受范围内")

    # 6. 质量检查 - 避免负面谐音
    negative_sounds = ['死', '笨', '傻', '坏', '恶', '鬼', '怪', '丑', '脏', '穷']
    for sound in negative_sounds:
        if sound in name:
            return False, f"名字包含不当字词：{sound}"

    return True, "名字验证通过"

def normalize_character_name(name: str) -> str:
    """
    标准化角色名字格式

    Args:
        name: 原始名字

    Returns:
        标准化后的名字
    """
    if not name:
        return name

    # 去除前后空格
    name = name.strip()

    # 去除内部多余空格
    name = re.sub(r'\s+', '', name)

    # 确保首字母大写（对于中文来说无需操作，但保留接口）
    if name and not name[0].isupper():
        # 对于中文，检查是否为英文字母
        if name[0].isalpha():
            name = name[0].upper() + name[1:]

    return name

def check_name_consistency(name: str, traits: dict) -> tuple[bool, str]:
    """
    检查名字与角色特征的一致性

    Args:
        name: 角色名字
        traits: 角色特征字典

    Returns:
        (是否一致, 错误信息)
    """
    if not traits:
        return True, "无特征信息，跳过一致性检查"

    # 性别一致性检查
    if 'gender' in traits:
        gender = traits['gender']
        is_valid, msg = validate_character_name(name, {'gender': gender})
        if not is_valid:
            return False, f"性别一致性检查失败：{msg}"

    # 年龄一致性检查
    if 'age' in traits:
        age = traits['age']
        if isinstance(age, (int, float)) and age < 18:
            # 检查是否有过于成熟的名字
            mature_chars = ['德', '仁', '义', '礼', '智', '信', '忠', '孝']
            if any(char in name for char in mature_chars):
                logging.warning(f"年轻角色（{age}岁）使用了较成熟的名字：{name}")
        elif isinstance(age, (int, float)) and age > 60:
            # 检查是否过于年轻化的名字
            young_chars = ['萌', '可爱', '甜', '乐', '欢']
            if any(char in name for char in young_chars):
                logging.warning(f"年长角色（{age}岁）使用了较年轻化的名字：{name}")

    # 文化背景一致性检查
    if 'cultural_background' in traits:
        background = traits['cultural_background']
        if '西方' in background:
            # 如果角色是西方背景，中文名字可能不太合适
            logging.warning(f"西方背景角色使用了中文名字：{name}")

    return True, "名字一致性检查通过"

# 角色名字注册表 - 用于跨章节名字一致性
character_name_registry = {}

def get_or_create_character_name(character_id: str, traits: dict = None) -> str:
    """
    获取或创建角色名字，确保跨章节一致性

    Args:
        character_id: 角色唯一标识
        traits: 角色特征，用于生成新名字

    Returns:
        角色名字
    """
    global character_name_registry

    # 如果角色已存在，返回已保存的名字
    if character_id in character_name_registry:
        logging.info(f"使用已存在的角色名字：{character_name_registry[character_id]}")
        return character_name_registry[character_id]

    # 如果是新角色，需要生成名字
    if traits:
        # 这里可以调用AI生成名字的逻辑
        # 暂时返回一个基于ID的默认名字
        default_name = f"角色{character_id[-3:]}"
        character_name_registry[character_id] = default_name
        logging.info(f"为新角色生成默认名字：{default_name}")
        return default_name
    else:
        # 如果没有特征信息，使用简单默认名字
        default_name = f"待定角色"
        character_name_registry[character_id] = default_name
        logging.warning(f"无特征信息，使用默认名字：{default_name}")
        return default_name

def save_character_name_registry(project_path: str):
    """
    保存角色名字注册表到项目文件

    Args:
        project_path: 项目路径
    """
    global character_name_registry

    try:
        registry_file = os.path.join(project_path, "character_names.json")
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(character_name_registry, f, ensure_ascii=False, indent=2)
        logging.info(f"角色名字注册表已保存到：{registry_file}")
    except Exception as e:
        logging.error(f"保存角色名字注册表失败：{e}")

def load_character_name_registry(project_path: str):
    """
    从项目文件加载角色名字注册表

    Args:
        project_path: 项目路径
    """
    global character_name_registry

    try:
        registry_file = os.path.join(project_path, "character_names.json")
        if os.path.exists(registry_file):
            with open(registry_file, 'r', encoding='utf-8') as f:
                character_name_registry = json.load(f)
            logging.info(f"角色名字注册表已加载，包含 {len(character_name_registry)} 个角色")
    except Exception as e:
        logging.error(f"加载角色名字注册表失败：{e}")
        character_name_registry = {}
