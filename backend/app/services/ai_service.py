import json
from typing import List, Optional
import httpx
from openai import OpenAI
from app.config import settings

MULTIMODAL_EMBEDDING_MODELS = {"qwen3-vl-embedding", "qwen2.5-vl-embedding"}


def _is_multimodal_model(model: str) -> bool:
    if model in MULTIMODAL_EMBEDDING_MODELS:
        return True
    if model.startswith("tongyi-embedding-vision"):
        return True
    return False

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
    print(f"[AI] organize_content 入参: raw_content长度={len(raw_content)}, model={settings.OPENAI_MODEL}, base_url={settings.OPENAI_BASE_URL}")
    print(f"[AI] organize_content 完整prompt: {prompt[:500]}...")
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
        print(f"[AI] organize_content response_format不支持, 降级重试: {e}")
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个知识管理助手，擅长整理和分析各种类型的内容。请始终以纯 JSON 格式返回结果。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
    result_text = response.choices[0].message.content.strip()
    print(f"[AI] organize_content 原始返回(前1000字符): {result_text[:1000]}")
    print(f"[AI] organize_content usage: prompt_tokens={getattr(response.usage, 'prompt_tokens', None)}, completion_tokens={getattr(response.usage, 'completion_tokens', None)}, finish_reason={response.choices[0].finish_reason}")
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
        result_text = result_text.strip()
    try:
        parsed = json.loads(result_text)
    except json.JSONDecodeError:
        print(f"[AI] organize_content JSON解析失败, 尝试提取花括号内容, 原始文本(前500字符): {result_text[:500]}")
        start = result_text.find("{")
        end = result_text.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(result_text[start:end])
        else:
            print(f"[AI] organize_content 无法提取JSON, 完整返回内容: {result_text}")
            raise
    if not isinstance(parsed, dict):
        print(f"[AI] organize_content 返回类型异常: {type(parsed)}, 内容: {str(parsed)[:500]}")
        raise ValueError(f"AI 返回了非 dict 类型: {type(parsed)}, 内容: {str(parsed)[:200]}")
    print(f"[AI] organize_content 解析成功: title={parsed.get('title')}, category={parsed.get('suggested_category')}, tags={parsed.get('suggested_tags')}")
    return parsed

def research_topic(topic: str, existing_content: str = "") -> str:
    prompt = RESEARCH_PROMPT.format(
        existing_content=existing_content or "暂无已有知识内容",
        topic=topic,
    )
    print(f"[AI] research_topic 入参: topic={topic}, existing_content长度={len(existing_content)}, model={settings.OPENAI_MODEL}")
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的研究助手，擅长对各种主题进行深度调研和分析。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
    result = response.choices[0].message.content.strip()
    print(f"[AI] research_topic usage: prompt_tokens={getattr(response.usage, 'prompt_tokens', None)}, completion_tokens={getattr(response.usage, 'completion_tokens', None)}, finish_reason={response.choices[0].finish_reason}")
    print(f"[AI] research_topic 返回(前500字符): {result[:500]}")
    return result


def expand_note(title: str, content: str) -> str:
    prompt = EXPAND_PROMPT.format(title=title, content=content)
    print(f"[AI] expand_note 入参: title={title}, content长度={len(content)}, model={settings.OPENAI_MODEL}")
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "你是一个知识扩展助手，擅长基于已有内容进行知识延伸和调研。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
    result = response.choices[0].message.content.strip()
    print(f"[AI] expand_note usage: prompt_tokens={getattr(response.usage, 'prompt_tokens', None)}, completion_tokens={getattr(response.usage, 'completion_tokens', None)}, finish_reason={response.choices[0].finish_reason}")
    print(f"[AI] expand_note 返回(前500字符): {result[:500]}")
    return result


EMBEDDING_DIMENSION = 1024


def generate_embedding(text: str) -> List[float]:
    model = settings.OPENAI_EMBEDDING_MODEL
    print(f"[AI] generate_embedding 入参: text长度={len(text)}, model={model}, base_url={settings.OPENAI_EMBEDDING_BASE_URL}, is_multimodal={_is_multimodal_model(model)}")

    if _is_multimodal_model(model):
        return _generate_multimodal_embedding(text, model)

    return _generate_text_embedding(text, model)


def _generate_multimodal_embedding(text: str, model: str) -> List[float]:
    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding"
    payload = {
        "model": model,
        "input": {
            "contents": [{"text": text}]
        },
        "parameters": {
            "dimension": EMBEDDING_DIMENSION,
        },
    }
    print(f"[AI] _generate_multimodal_embedding 请求: url={url}, model={model}, dimension={EMBEDDING_DIMENSION}, text长度={len(text)}")
    resp = httpx.post(url, headers={
        "Authorization": f"Bearer {settings.OPENAI_EMBEDDING_API_KEY}",
        "Content-Type": "application/json",
    }, json=payload, timeout=120)
    data = resp.json()
    print(f"[AI] _generate_multimodal_embedding 响应状态码: {resp.status_code}")
    if resp.status_code != 200 or "output" not in data:
        print(f"[AI] _generate_multimodal_embedding 失败, 完整响应: {data}")
        raise RuntimeError(f"DashScope multimodal embedding API 调用失败: {data}")
    embedding = data["output"]["embeddings"][0]["embedding"]
    print(f"[AI] _generate_multimodal_embedding 成功, 维度={len(embedding)}, request_id={data.get('request_id')}")
    return embedding


def _generate_text_embedding(text: str, model: str) -> List[float]:
    print(f"[AI] _generate_text_embedding 请求: model={model}, dimensions={EMBEDDING_DIMENSION}, text长度={len(text)}, base_url={settings.OPENAI_EMBEDDING_BASE_URL}")
    response = embedding_client.embeddings.create(
        model=model,
        input=text,
        dimensions=EMBEDDING_DIMENSION,
    )
    embedding = response.data[0].embedding
    print(f"[AI] _generate_text_embedding 成功, 维度={len(embedding)}, model={model}, usage={getattr(response.usage, 'total_tokens', None)}")
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(f"Embedding 维度不匹配: 期望 {EMBEDDING_DIMENSION}, 实际 {len(embedding)}")
    return embedding
