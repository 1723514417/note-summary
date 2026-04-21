from typing import List
import os
import traceback

# 跳过ChromaDB初始化，避免依赖问题
def add_to_vector(note_id: int, text: str, embedding: List[float]):
    try:
        print(f"[DEBUG] add_to_vector 成功, note_id={note_id} (跳过ChromaDB)")
    except Exception as e:
        print(f"[DEBUG] add_to_vector 失败: {e}")
        print(traceback.format_exc())


def search_similar(query_embedding: List[float], limit: int = 10) -> List[dict]:
    print(f"[DEBUG] search_similar 开始, limit={limit} (跳过ChromaDB)")
    try:
        print(f"[DEBUG] search_similar 完成, 返回 0 条 (跳过ChromaDB)")
        return []
    except Exception as e:
        print(f"[DEBUG] search_similar 失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def delete_from_vector(note_id: int):
    try:
        print(f"[DEBUG] delete_from_vector 成功, note_id={note_id} (跳过ChromaDB)")
    except Exception:
        pass
