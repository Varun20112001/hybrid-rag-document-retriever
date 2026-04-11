from dataclasses import asdict
from uuid import UUID
from uuid import uuid4

from core.application.dto import (
    DocumentStatusOutput,
    SearchInput,
    SearchOutput,
    SearchResultItem,
    UploadDocumentInput,
    UploadDocumentOutput,
)
from core.application.interfaces import (
    ChunkRepository,
    Chunker,
    DocumentRepository,
    EmbeddingService,
    FusionService,
    LexicalRetriever,
    RerankerService,
    TaskDispatcher,
    TextExtractor,
    VectorRetriever,
)
from core.domain.entities import Chunk, Document, SearchQuery
from core.domain.value_objects import ChunkMetadata, DocumentStatus


class UploadDocumentUseCase:
    def __init__(self, document_repo: DocumentRepository, task_dispatcher: TaskDispatcher):
        self.document_repo = document_repo
        self.task_dispatcher = task_dispatcher

    def execute(self, data: UploadDocumentInput) -> UploadDocumentOutput:
        document = Document(
            id=uuid4(),
            filename=data.filename,
            content_type=data.content_type,
            size=data.size,
            status=DocumentStatus.PENDING,
            storage_path=data.storage_path,
        )
        created = self.document_repo.create(document)
        self.task_dispatcher.dispatch_document_processing(created.id)
        return UploadDocumentOutput(document_id=created.id, status=created.status.value)


class GetDocumentStatusUseCase:
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo

    def execute(self, document_id):
        if isinstance(document_id, str):
            document_id = UUID(document_id)
        document = self.document_repo.get(document_id)
        if not document:
            return None
        return DocumentStatusOutput(document_id=document.id, status=document.status.value, error_message=document.error_message)


class ProcessDocumentUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        extractor: TextExtractor,
        chunker: Chunker,
        embedding_service: EmbeddingService,
    ):
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.extractor = extractor
        self.chunker = chunker
        self.embedding_service = embedding_service

    def execute(self, document_id):
        if isinstance(document_id, str):
            document_id = UUID(document_id)
        document = self.document_repo.get(document_id)
        if not document:
            raise ValueError("Document not found")

        self.document_repo.update_status(document_id, DocumentStatus.PROCESSING.value)

        try:
            text = self.extractor.extract(document.storage_path)
            chunks = self.chunker.split(text, source=document.filename)
            vectors = self.embedding_service.embed([c["text"] for c in chunks]) if chunks else []

            mapped = []
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                mapped.append(
                    Chunk(
                        id=uuid4(),
                        document_id=document.id,
                        chunk_index=idx,
                        text=chunk["text"],
                        metadata=ChunkMetadata(source=document.filename, extra=chunk.get("metadata", {})),
                        token_count=len(chunk["text"].split()),
                        embedding=vector,
                    )
                )

            self.chunk_repo.clear_for_document(document.id)
            self.chunk_repo.bulk_create(mapped)
            self.document_repo.update_status(document.id, DocumentStatus.COMPLETED.value)
        except Exception as exc:  # noqa: BLE001
            self.document_repo.update_status(document.id, DocumentStatus.FAILED.value, str(exc))
            raise


class SearchDocumentsUseCase:
    def __init__(
        self,
        lexical_retriever: LexicalRetriever,
        vector_retriever: VectorRetriever,
        fusion_service: FusionService,
        reranker: RerankerService,
        embedding_service: EmbeddingService,
        mmr_lambda: float = 0.5,
        rrf_k: int = 60,
    ):
        self.lexical_retriever = lexical_retriever
        self.vector_retriever = vector_retriever
        self.fusion_service = fusion_service
        self.reranker = reranker
        self.embedding_service = embedding_service
        self.mmr_lambda = mmr_lambda
        self.rrf_k = rrf_k

    def execute(self, data: SearchInput) -> SearchOutput:
        query = SearchQuery(query=data.query, mode=data.mode, top_k=data.top_k, filters=data.filters)
        lexical = self.lexical_retriever.retrieve(query, candidate_k=max(data.top_k * 5, 20))
        semantic = self.vector_retriever.retrieve(query, candidate_k=max(data.top_k * 5, 20))
        semantic = self.vector_retriever.mmr(
            query_embedding=self.embedding_service.embed_query(data.query),
            results=semantic,
            top_k=max(data.top_k * 3, 10),
            lambda_mult=self.mmr_lambda,
        )

        if data.mode == "keyword":
            final = lexical[: data.top_k]
        elif data.mode == "semantic":
            final = self.reranker.rerank(data.query, semantic, data.top_k)
        else:
            fused = self.fusion_service.fuse(lexical, semantic, k=self.rrf_k)
            final = self.reranker.rerank(data.query, fused, data.top_k)

        return SearchOutput(
            query=data.query,
            mode=data.mode,
            results=[
                SearchResultItem(
                    chunk_id=item.chunk_id,
                    document_id=item.document_id,
                    text=item.text,
                    metadata=item.metadata,
                    **asdict(item.scores),
                )
                for item in final
            ],
        )
