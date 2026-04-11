from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F
from pgvector.django import CosineDistance
from rank_bm25 import BM25Okapi

from core.application.interfaces import ChunkRepository, DocumentRepository
from core.domain.entities import Chunk, Document, SearchQuery as DomainSearchQuery, SearchResult
from core.domain.value_objects import DocumentStatus, ScoreBundle
from document.models import DocumentChunkModel, DocumentModel


class DjangoDocumentRepository(DocumentRepository):
    def create(self, document: Document) -> Document:
        row = DocumentModel.objects.create(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size=document.size,
            status=document.status.value,
            storage_path=document.storage_path,
        )
        return self._to_domain(row)

    def get(self, document_id):
        try:
            return self._to_domain(DocumentModel.objects.get(id=document_id))
        except DocumentModel.DoesNotExist:
            return None

    def update_status(self, document_id, status: str, error_message: str | None = None) -> None:
        DocumentModel.objects.filter(id=document_id).update(status=status, error_message=error_message)

    @staticmethod
    def _to_domain(row: DocumentModel) -> Document:
        return Document(
            id=row.id,
            filename=row.filename,
            content_type=row.content_type,
            size=row.size,
            status=DocumentStatus(row.status),
            storage_path=row.storage_path,
            error_message=row.error_message,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class DjangoChunkRepository(ChunkRepository):
    def bulk_create(self, chunks: list[Chunk]) -> None:
        rows = [
            DocumentChunkModel(
                id=item.id,
                document_id=item.document_id,
                chunk_index=item.chunk_index,
                text=item.text,
                metadata={"source": item.metadata.source, **item.metadata.extra},
                token_count=item.token_count,
                embedding=item.embedding,
            )
            for item in chunks
        ]
        DocumentChunkModel.objects.bulk_create(rows)

        # materialize tsvector after insert
        DocumentChunkModel.objects.filter(id__in=[item.id for item in chunks]).update(search_vector=SearchVector("text"))

    def clear_for_document(self, document_id) -> None:
        DocumentChunkModel.objects.filter(document_id=document_id).delete()


class PostgresLexicalRetriever:
    def retrieve(self, query: DomainSearchQuery, candidate_k: int) -> list[SearchResult]:
        search_query = SearchQuery(query.query)
        rows = list(
            DocumentChunkModel.objects.annotate(rank=SearchRank(F("search_vector"), search_query))
            .filter(rank__gt=0.0)
            .order_by("-rank")[:candidate_k]
        )
        if not rows:
            return []

        bm25 = BM25Okapi([row.text.split() for row in rows])
        bm25_scores = bm25.get_scores(query.query.split())

        results = []
        for row, score in zip(rows, bm25_scores):
            results.append(
                SearchResult(
                    chunk_id=row.id,
                    document_id=row.document_id,
                    text=row.text,
                    metadata=row.metadata,
                    scores=ScoreBundle(bm25_score=float(score)),
                )
            )
        return sorted(results, key=lambda item: item.scores.bm25_score, reverse=True)


class PgvectorRetriever:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service

    def retrieve(self, query: DomainSearchQuery, candidate_k: int) -> list[SearchResult]:
        query_vec = self.embedding_service.embed_query(query.query)
        rows = (
            DocumentChunkModel.objects.exclude(embedding=None)
            .annotate(distance=CosineDistance("embedding", query_vec))
            .order_by("distance")[:candidate_k]
        )
        results = []
        for row in rows:
            results.append(
                SearchResult(
                    chunk_id=row.id,
                    document_id=row.document_id,
                    text=row.text,
                    metadata=row.metadata,
                    scores=ScoreBundle(vector_score=(1.0 - float(row.distance))),
                )
            )
        return results

    def mmr(self, query_embedding: list[float], results: list[SearchResult], top_k: int, lambda_mult: float):
        if len(results) <= top_k:
            return results

        selected = []
        candidates = results.copy()
        while candidates and len(selected) < top_k:
            best = None
            best_score = float("-inf")
            for candidate in candidates:
                relevance = candidate.scores.vector_score
                novelty = 0.0
                if selected:
                    novelty = max(self._jaccard(candidate.text, picked.text) for picked in selected)
                score = lambda_mult * relevance - (1 - lambda_mult) * novelty
                if score > best_score:
                    best_score = score
                    best = candidate
            selected.append(best)
            candidates.remove(best)
        return selected

    @staticmethod
    def _jaccard(a: str, b: str) -> float:
        left = set(a.lower().split())
        right = set(b.lower().split())
        if not left or not right:
            return 0.0
        return len(left & right) / len(left | right)
