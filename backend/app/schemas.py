from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NoteCreate(BaseModel):
    raw_content: str
    category_id: Optional[int] = None
    source_type: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    organized_content: Optional[str] = None
    summary: Optional[str] = None
    category_id: Optional[int] = None
    keywords: Optional[str] = None
    source_type: Optional[str] = None
    research_content: Optional[str] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    raw_content: str
    organized_content: Optional[str] = None
    summary: Optional[str] = None
    category_id: Optional[int] = None
    keywords: Optional[str] = None
    source_type: Optional[str] = None
    research_content: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List["TagResponse"] = []

    class Config:
        from_attributes = True


class NoteListItem(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    category_id: Optional[int] = None
    keywords: Optional[str] = None
    source_type: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    children: List["CategoryResponse"] = []

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str


class OrganizeRequest(BaseModel):
    raw_content: str


class OrganizeResponse(BaseModel):
    title: str
    organized_content: str
    summary: str
    suggested_category: str
    suggested_tags: List[str]
    source_type: str
    keywords: str


class ResearchRequest(BaseModel):
    note_id: Optional[int] = None
    topic: Optional[str] = None


class ResearchResponse(BaseModel):
    research_content: str
    related_notes: List[NoteListItem] = []


class SearchResult(BaseModel):
    notes: List[NoteListItem]
    total: int


NoteResponse.model_rebuild()
CategoryResponse.model_rebuild()
