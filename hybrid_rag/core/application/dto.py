from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class UploadDocumentInput:
    filename: str
    content_type: str
    size: int
    storage_path: str


@dataclass
class UploadDocumentOutput:
    document_id: UUID
    status: str


@dataclass
class DocumentStatusOutput:
    document_id: UUID
    status: str
    error_message: str | None


@dataclass
class SearchInput:
    query: str
    mode: str = "hybrid"
    top_k: int = 10
    filters: dict = field(default_factory=dict)


@dataclass
class SearchResultItem:
    chunk_id: UUID
    document_id: UUID
    text: str
    metadata: dict
    bm25_score: float
    vector_score: float
    rrf_score: float
    rerank_score: float


@dataclass
class SearchOutput:
    query: str
    mode: str
    results: list[SearchResultItem]
