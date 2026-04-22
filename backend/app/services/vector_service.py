from typing import List
import struct
import threading
import traceback

import numpy as np
from sqlalchemy import text
from app.database import engine, is_postgres


if is_postgres():
    pass


class VectorIndex:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._mutex = threading.Lock()
        self._dirty = True
        self._note_ids: List[int] = []
        self._matrix: np.ndarray | None = None

    @classmethod
    def get(cls) -> "VectorIndex":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def mark_dirty(self):
        with self._mutex:
            self._dirty = True

    def _ensure_loaded(self):
        with self._mutex:
            if not self._dirty and self._matrix is not None:
                return
            self._load_from_db()

    def _load_from_db(self):
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT note_id, embedding FROM note_embeddings")
            )
            rows = result.fetchall()

        if not rows:
            self._note_ids = []
            self._matrix = None
            self._dirty = False
            return

        self._note_ids = [row[0] for row in rows]
        vectors = np.stack([_bytes_to_embedding(row[1]) for row in rows])
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        self._matrix = vectors / norms
        self._dirty = False

    def search(self, query_embedding: List[float], limit: int = 10) -> List[dict]:
        self._ensure_loaded()

        if self._matrix is None or len(self._note_ids) == 0:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []
        query_vec = query_vec / query_norm

        similarities = self._matrix @ query_vec
        top_indices = np.argsort(similarities)[::-1][:limit]

        return [
            {"id": self._note_ids[int(i)], "distance": 1 - float(similarities[i])}
            for i in top_indices
        ]


def _embedding_to_bytes(embedding: List[float]) -> bytes:
    return struct.pack(f"{len(embedding)}f", *embedding)


def _bytes_to_embedding(data: bytes) -> np.ndarray:
    count = len(data) // 4
    return np.array(struct.unpack(f"{count}f", data), dtype=np.float32)


def _embedding_to_pg_str(embedding: List[float]) -> str:
    return "[" + ",".join(str(x) for x in embedding) + "]"


def add_to_vector(note_id: int, content: str, embedding: List[float]):
    try:
        if is_postgres():
            embedding_str = _embedding_to_pg_str(embedding)
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO note_embeddings (note_id, embedding)
                        VALUES (:note_id, CAST(:embedding AS vector))
                        ON CONFLICT (note_id) DO UPDATE SET embedding = CAST(EXCLUDED.embedding AS vector)
                    """),
                    {"note_id": note_id, "embedding": embedding_str},
                )
        else:
            blob = _embedding_to_bytes(embedding)
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "INSERT OR REPLACE INTO note_embeddings (note_id, embedding) "
                        "VALUES (:note_id, :embedding)"
                    ),
                    {"note_id": note_id, "embedding": blob},
                )
        VectorIndex.get().mark_dirty()
        print(f"[DEBUG] add_to_vector 成功, note_id={note_id}")
    except Exception as e:
        print(f"[DEBUG] add_to_vector 失败: {e}")
        print(traceback.format_exc())


def search_similar(query_embedding: List[float], limit: int = 10) -> List[dict]:
    print(f"[DEBUG] search_similar 开始, limit={limit}")
    try:
        if is_postgres():
            return _search_similar_pg(query_embedding, limit)
        else:
            results = VectorIndex.get().search(query_embedding, limit)
            print(f"[DEBUG] search_similar 完成, 返回 {len(results)} 条")
            return results
    except Exception as e:
        print(f"[DEBUG] search_similar 失败: {e}")
        print(traceback.format_exc())
        return []


def _search_similar_pg(query_embedding: List[float], limit: int = 10) -> List[dict]:
    embedding_str = _embedding_to_pg_str(query_embedding)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT note_id, embedding <=> CAST(:query AS vector) AS distance
                FROM note_embeddings
                ORDER BY embedding <=> CAST(:query AS vector)
                LIMIT :limit
            """),
            {"query": embedding_str, "limit": limit},
        )
        rows = result.fetchall()
    results = [{"id": row[0], "distance": float(row[1])} for row in rows]
    print(f"[DEBUG] search_similar (pgvector) 完成, 返回 {len(results)} 条")
    return results


def delete_from_vector(note_id: int):
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM note_embeddings WHERE note_id = :note_id"),
                {"note_id": note_id},
            )
        VectorIndex.get().mark_dirty()
        print(f"[DEBUG] delete_from_vector 成功, note_id={note_id}")
    except Exception as e:
        print(f"[DEBUG] delete_from_vector 失败: {e}")
