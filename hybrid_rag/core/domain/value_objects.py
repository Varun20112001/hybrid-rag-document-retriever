from dataclasses import dataclass, field
from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class ScoreBundle:
    bm25_score: float = 0.0
    vector_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0


@dataclass
class ChunkMetadata:
    source: str | None = None
    extra: dict = field(default_factory=dict)
