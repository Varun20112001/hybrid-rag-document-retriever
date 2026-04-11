import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from pgvector.django import IvfflatIndex, VectorField



class DocumentChunkModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document = models.ForeignKey(
        to="document.DocumentModel", on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    metadata = models.JSONField(default=dict)
    token_count = models.IntegerField(default=0)
    search_vector = SearchVectorField(null=True)
    embedding = VectorField(dimensions=384, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document_chunks"
        verbose_name = "Document Chunk"
        verbose_name_plural = "Document Chunks"
        ordering = ["document", "chunk_index"]
        constraints = [models.UniqueConstraint(fields=["document", "chunk_index"], name="uniq_doc_chunk_idx")]
        indexes = [
            GinIndex(fields=["search_vector"], name="chunks_search_vector_gin"),
            IvfflatIndex(
                name="chunks_embedding_ivfflat",
                fields=["embedding"],
                lists=100,
                opclasses=["vector_cosine_ops"],
            ),
        ]
