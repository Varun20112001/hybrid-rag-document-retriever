from django.db import models
import uuid

class ProcessingRunModel(models.Model):
    STATUS_STARTED = "STARTED"
    STATUS_RETRY = "RETRY"
    STATUS_FAILED = "FAILED"
    STATUS_FINISHED = "FINISHED"
    STATUS_CHOICES = (
        (STATUS_STARTED, "Started"),
        (STATUS_RETRY, "Retry"),
        (STATUS_FAILED, "Failed"),
        (STATUS_FINISHED, "Finished"),
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document = models.ForeignKey(
        to="document.DocumentModel", 
        on_delete=models.CASCADE, 
        related_name="processing_runs"
    )
    task_id = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_STARTED)
    retries = models.IntegerField(default=0)
    chunk_count = models.IntegerField(default=0)
    embed_seconds = models.FloatField(default=0.0)
    total_seconds = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    failure_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "processing_runs"
        verbose_name = "Processing Run"
        verbose_name_plural = "Processing Runs"
        ordering = ["-started_at"]
