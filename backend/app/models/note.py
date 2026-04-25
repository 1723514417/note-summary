from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base, is_postgres
import datetime
import pytz

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class NoteLink(Base):
    __tablename__ = "note_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("source_id", "target_id", name="uq_note_link"),)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    raw_content = Column(Text, nullable=False)
    organized_content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    keywords = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=True)
    research_content = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    is_starred = Column(Boolean, default=False, nullable=False, index=True)
    is_pinned = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(pytz.timezone('Asia/Shanghai')))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(pytz.timezone('Asia/Shanghai')), onupdate=lambda: datetime.datetime.now(pytz.timezone('Asia/Shanghai')))

    category = relationship("Category", back_populates="notes")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")
    owner = relationship("User", back_populates="notes")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(pytz.timezone('Asia/Shanghai')))

    parent = relationship("Category", remote_side=[id], backref="children")
    notes = relationship("Note", back_populates="category")
    owner = relationship("User", back_populates="categories")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    notes = relationship("Note", secondary=note_tags, back_populates="tags")


if is_postgres():
    from pgvector.sqlalchemy import Vector

    class NoteEmbedding(Base):
        __tablename__ = "note_embeddings"

        note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True)
        embedding = Column(Vector(2560), nullable=False)
