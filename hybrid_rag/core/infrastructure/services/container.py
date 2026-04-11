import os

from core.application.use_cases import (
    GetDocumentStatusUseCase,
    ProcessDocumentUseCase,
    SearchDocumentsUseCase,
    UploadDocumentUseCase,
)
from core.infrastructure.adapters.chunker import LangchainChunker
from core.infrastructure.adapters.extract_embed import FileTextExtractor, HybridEmbeddingService
from core.infrastructure.adapters.fusion import RRFFusionService
from core.infrastructure.adapters.reranker import CrossEncoderReranker
from core.infrastructure.adapters.task_dispatcher import CeleryTaskDispatcher
from core.infrastructure.runtime.model_registry import ModelRegistry
from core.infrastructure.repositories.django_repositories import (
    DjangoChunkRepository,
    DjangoDocumentRepository,
    PgvectorRetriever,
    PostgresLexicalRetriever,
)

_EMBEDDING_SERVICE: HybridEmbeddingService | None = None
_RERANKER_SERVICE: CrossEncoderReranker | None = None


def _get_embedding_service() -> HybridEmbeddingService:
    global _EMBEDDING_SERVICE
    if _EMBEDDING_SERVICE is None:
        _EMBEDDING_SERVICE = HybridEmbeddingService(model=ModelRegistry.get_embedder())
    return _EMBEDDING_SERVICE


def _get_reranker_service() -> CrossEncoderReranker:
    global _RERANKER_SERVICE
    if _RERANKER_SERVICE is None:
        _RERANKER_SERVICE = CrossEncoderReranker(model=ModelRegistry.get_reranker())
    return _RERANKER_SERVICE


def build_upload_use_case() -> UploadDocumentUseCase:
    return UploadDocumentUseCase(
        document_repo=DjangoDocumentRepository(),
        task_dispatcher=CeleryTaskDispatcher(),
    )


def build_status_use_case() -> GetDocumentStatusUseCase:
    return GetDocumentStatusUseCase(document_repo=DjangoDocumentRepository())


def build_process_use_case() -> ProcessDocumentUseCase:
    return ProcessDocumentUseCase(
        document_repo=DjangoDocumentRepository(),
        chunk_repo=DjangoChunkRepository(),
        extractor=FileTextExtractor(),
        chunker=LangchainChunker(
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        ),
        embedding_service=_get_embedding_service(),
    )


def build_search_use_case() -> SearchDocumentsUseCase:
    embedding = _get_embedding_service()
    return SearchDocumentsUseCase(
        lexical_retriever=PostgresLexicalRetriever(),
        vector_retriever=PgvectorRetriever(embedding_service=embedding),
        fusion_service=RRFFusionService(),
        reranker=_get_reranker_service(),
        embedding_service=embedding,
        mmr_lambda=float(os.getenv("MMR_LAMBDA", "0.5")),
        rrf_k=int(os.getenv("RRF_K", "60")),
    )
