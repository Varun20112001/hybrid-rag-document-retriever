from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.entities import Chunk, Document, SearchQuery, SearchResult


class DocumentRepository(ABC):
    @abstractmethod
    def create(self, document: Document) -> Document: ...

    @abstractmethod
    def get(self, document_id: UUID) -> Document | None: ...

    @abstractmethod
    def update_status(
        self, document_id: UUID, status: str, error_message: str | None = None
    ) -> None: ...


class ChunkRepository(ABC):
    @abstractmethod
    def bulk_create(self, chunks: list[Chunk]) -> None: ...

    @abstractmethod
    def clear_for_document(self, document_id: UUID) -> None: ...


class TextExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> str: ...


class Chunker(ABC):
    @abstractmethod
    def split(self, text: str, source: str) -> list[dict]: ...


class EmbeddingService(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]: ...


class LexicalRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: SearchQuery, candidate_k: int) -> list[SearchResult]: ...


class VectorRetriever(ABC):
    @abstractmethod
    def retrieve(
        self, query: SearchQuery, candidate_k: int
    ) -> list[SearchResult]: ...

    @abstractmethod
    def mmr(
        self, query_embedding: list[float], 
        results: list[SearchResult], 
        top_k: int, lambda_mult: float
    ) -> list[SearchResult]: ...


class FusionService(ABC):
    @abstractmethod
    def fuse(self, lexical: list[SearchResult], semantic: list[SearchResult], k: int) -> list[SearchResult]: ...


class RerankerService(ABC):
    @abstractmethod
    def rerank(self, query: str, results: list[SearchResult], top_k: int) -> list[SearchResult]: ...


class TaskDispatcher(ABC):
    @abstractmethod
    def dispatch_document_processing(self, document_id: UUID) -> str: ...
