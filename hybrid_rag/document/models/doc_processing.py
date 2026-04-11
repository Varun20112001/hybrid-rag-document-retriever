from django.db import models
import uuid

class ProcessingRunModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document = models.ForeignKey(
        to="document.DocumentModel", 
        on_delete=models.CASCADE, 
        related_name="processing_runs"
    )
    task_id = models.CharField(max_length=255)
    retries = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "processing_runs"
        verbose_name = "Processing Run"
        verbose_name_plural = "Processing Runs"
        ordering = ["-started_at"]
