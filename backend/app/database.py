from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.config import settings
import os


db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
db_dir = os.path.dirname(db_path)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    f"sqlite:///{db_path}",
    echo=False,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            __import__("sqlalchemy").text(
                "CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5("
                "title, raw_content, organized_content, summary, keywords,"
                "content=notes, content_rowid=id)"
            )
        )
        conn.execute(
            __import__("sqlalchemy").text(
                "CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN"
                " INSERT INTO notes_fts(rowid, title, raw_content, organized_content, summary, keywords)"
                " VALUES (new.id, new.title, new.raw_content, new.organized_content, new.summary, new.keywords);"
                "END"
            )
        )
        conn.execute(
            __import__("sqlalchemy").text(
                "CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN"
                " INSERT INTO notes_fts(notes_fts, rowid, title, raw_content, organized_content, summary, keywords)"
                " VALUES ('delete', old.id, old.title, old.raw_content, old.organized_content, old.summary, old.keywords);"
                "END"
            )
        )
        conn.execute(
            __import__("sqlalchemy").text(
                "CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN"
                " INSERT INTO notes_fts(notes_fts, rowid, title, raw_content, organized_content, summary, keywords)"
                " VALUES ('delete', old.id, old.title, old.raw_content, old.organized_content, old.summary, old.keywords);"
                " INSERT INTO notes_fts(rowid, title, raw_content, organized_content, summary, keywords)"
                " VALUES (new.id, new.title, new.raw_content, new.organized_content, new.summary, new.keywords);"
                "END"
            )
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
