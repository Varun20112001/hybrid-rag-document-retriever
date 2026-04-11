from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from core.domain.value_objects import ChunkMetadata, DocumentStatus, ScoreBundle


@dataclass
class Document:
    id: UUID
    filename: str
    content_type: str
    size: int
    status: DocumentStatus
    storage_path: str
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Chunk:
    id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    metadata: ChunkMetadata
    token_count: int
    embedding: list[float] | None


@dataclass
class SearchQuery:
    query: str
    mode: str
    top_k: int
    filters: dict


@dataclass
class SearchResult:
    chunk_id: UUID
    document_id: UUID
    text: str
    metadata: dict
    scores: ScoreBundle
