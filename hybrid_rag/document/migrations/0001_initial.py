# Generated manually for initial schema.

import uuid
import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
import pgvector.django.indexes
import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector"),
        migrations.CreateModel(
            name="DocumentModel",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("filename", models.CharField(max_length=512)),
                ("content_type", models.CharField(max_length=128)),
                ("size", models.BigIntegerField()),
                ("status", models.CharField(db_index=True, max_length=16)),
                ("storage_path", models.CharField(max_length=1024)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "documents"},
        ),
        migrations.CreateModel(
            name="DocumentChunkModel",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("chunk_index", models.IntegerField()),
                ("text", models.TextField()),
                ("metadata", models.JSONField(default=dict)),
                ("token_count", models.IntegerField(default=0)),
                ("search_vector", django.contrib.postgres.search.SearchVectorField(null=True)),
                ("embedding", pgvector.django.vector.VectorField(dimensions=384, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "document",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="document.documentmodel"),
                ),
            ],
            options={
                "db_table": "document_chunks",
                "constraints": [
                    models.UniqueConstraint(fields=("document", "chunk_index"), name="uniq_doc_chunk_idx")
                ],
                "indexes": [
                    django.contrib.postgres.indexes.GinIndex(fields=["search_vector"], name="chunks_search_vector_gin"),
                    pgvector.django.indexes.IvfflatIndex(
                        fields=["embedding"],
                        lists=100,
                        name="chunks_embedding_ivfflat",
                        opclasses=["vector_cosine_ops"],
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProcessingRunModel",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("task_id", models.CharField(max_length=255)),
                ("retries", models.IntegerField(default=0)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("failure_reason", models.TextField(blank=True, null=True)),
                (
                    "document",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="processing_runs", to="document.documentmodel"),
                ),
            ],
            options={"db_table": "processing_runs"},
        ),
    ]
