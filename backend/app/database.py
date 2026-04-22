from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.config import settings
import os


database_url = settings.DATABASE_URL

if database_url.startswith("sqlite"):
    db_path = database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        database_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def _set_search_path(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    if database_url.startswith("sqlite"):
        _init_sqlite()
    else:
        _init_postgres()


def _init_postgres():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)


def _init_sqlite():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS note_embeddings ("
                "note_id INTEGER PRIMARY KEY,"
                "embedding BLOB NOT NULL,"
                "FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE)"
            )
        )
        conn.execute(
            text(
                "CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5("
                "title, raw_content, organized_content, summary, keywords,"
                "content=notes, content_rowid=id)"
            )
        )
        conn.execute(text(
            "CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN"
            " INSERT INTO notes_fts(rowid, title, raw_content, organized_content, summary, keywords)"
            " VALUES (new.id, new.title, new.raw_content, new.organized_content, new.summary, new.keywords);"
            "END"
        ))
        conn.execute(text(
            "CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN"
            " INSERT INTO notes_fts(notes_fts, rowid, title, raw_content, organized_content, summary, keywords)"
            " VALUES ('delete', old.id, old.title, old.raw_content, old.organized_content, old.summary, old.keywords);"
            "END"
        ))
        conn.execute(text(
            "CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN"
            " INSERT INTO notes_fts(notes_fts, rowid, title, raw_content, organized_content, summary, keywords)"
            " VALUES ('delete', old.id, old.title, old.raw_content, old.organized_content, old.summary, old.keywords);"
            " INSERT INTO notes_fts(rowid, title, raw_content, organized_content, summary, keywords)"
            " VALUES (new.id, new.title, new.raw_content, new.organized_content, new.summary, new.keywords);"
            "END"
        ))


def is_postgres() -> bool:
    return not database_url.startswith("sqlite")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
