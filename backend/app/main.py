from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db, SessionLocal
from app.routers import notes, search, categories, tags, ai, auth, stats
import os
import threading
import time


def _auto_purge_trash():
    while True:
        time.sleep(86400)
        try:
            from app.services.note_service import purge_expired_notes
            db = SessionLocal()
            try:
                count = purge_expired_notes(db, days=30)
                if count > 0:
                    print(f"[AUTO_PURGE] 已清理 {count} 条过期回收站笔记")
            finally:
                db.close()
        except Exception as e:
            print(f"[AUTO_PURGE] 清理失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    purge_thread = threading.Thread(target=_auto_purge_trash, daemon=True)
    purge_thread.start()
    yield


app = FastAPI(title="Note Summary - 个人知识库", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(search.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(ai.router)
app.include_router(stats.router)

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
