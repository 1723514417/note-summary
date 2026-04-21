import json
from typing import List, Optional
from openai import OpenAI
from app.config import settings

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    timeout=None,
)

embedding_client = OpenAI(
    api_key=settings.OPENAI_EMBEDDING_API_KEY,
    base_url=settings.OPENAI_EMBEDDING_BASE_URL,
    timeout=None,
)

ORGANIZE_PROMPT = """你是一个专业的知识管理助手。用户会给你一段原始内容，请你对它进行整理和分析。

请按以下 JSON 格式返回结果（不要包含任何其他文字，只返回 JSON）：

{{
    "title": "为这段内容生成一个简洁明确的标题",
    "organized_content": "将原始内容整理为结构化的内容，使用 Markdown 格式，添加适当的标题层级、列表、强调等",
    "summary": "用1-3句话总结这段内容的核心要点",
    "suggested_category": "建议的分类，如：生活记录、学习笔记、技术知识、读书笔记、工作日志、个人感想、待办事项、灵感创意 等",
    "suggested_tags": ["标签1", "标签2", "标签3"],
    "source_type": "判断内容类型：life(生活)、thought(感想)、knowledge(知识)、todo(待办)、idea(灵感)、work(工作)",
    "keywords": "关键词1,关键词2,关键词3"
}}

原始内容：
{content}"""

RESEARCH_PROMPT = """你是一个专业的研究助手。基于以下已有知识内容，对指定主题进行深度调研和分析。

已有知识内容：
{existing_content}

调研主题：{topic}

请生成一份详细的调研报告，包含：
1. 背景概述
2. 核心要点分析
3. 与已有知识的关联
4. 深度见解和扩展知识
5. 总结

请用 Markdown 格式输出。"""

EXPAND_PROMPT = """你是一个知识扩展助手。用户有一条笔记，请基于这条笔记的内容，帮助用户进行相关知识扩展和调研。

笔记标题：{title}
笔记内容：
{content}

请生成扩展调研内容，包含：
1. 相关概念解释
2. 知识延伸
3. 实际应用或案例
4. 进一步学习的建议

请用 Markdown 格式输出。"""


def organize_content(raw_content: str) -> dict:
    prompt = ORGANIZE_PROMPT.format(content=raw_content)
    print(f"[DEBUG] 调用 AI API, model={settings.OPENAI_MODEL}, base_url={settings.OPENAI_BASE_URL}")
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个知识管理助手，擅长整理和分析各种类型的内容。请始终以纯 JSON 格式返回结果。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        print(f"[DEBUG] response_format 不支持, 降级重试: {e}")
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个知识管理助手，擅长整理和分析各种类型的内容。请始终以纯 JSON 格式返回结果。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
        result_text = result_text.strip()
    return json.loads(result_text)


def research_topic(topic: str, existing_content: str = "") -> str:
    prompt = RESEARCH_PROMPT.format(
        existing_content=existing_content or "暂无已有知识内容",
        topic=topic,
    )
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的研究助手，擅长对各种主题进行深度调研和分析。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def expand_note(title: str, content: str) -> str:
    prompt = EXPAND_PROMPT.format(title=title, content=content)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "你是一个知识扩展助手，擅长基于已有内容进行知识延伸和调研。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def generate_embedding(text: str) -> List[float]:
    response = embedding_client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding
