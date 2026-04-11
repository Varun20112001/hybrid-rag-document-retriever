from celery import shared_task
from django.utils import timezone
import logging

from core.infrastructure.services.container import build_process_use_case
from document.models import ProcessingRunModel

logger = logging.getLogger(__name__)


def _is_recoverable_error(exc: Exception) -> bool:
    recoverable_types = (ConnectionError, TimeoutError, OSError)
    non_recoverable_types = (ValueError, FileNotFoundError)
    if isinstance(exc, non_recoverable_types):
        return False
    return isinstance(exc, recoverable_types)


@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    run = ProcessingRunModel.objects.create(
        document_id=document_id,
        task_id=self.request.id,
        status=ProcessingRunModel.STATUS_STARTED,
        retries=self.request.retries,
    )
    use_case = build_process_use_case()
    try:
        metrics = use_case.execute(document_id)
        run.status = ProcessingRunModel.STATUS_FINISHED
        run.chunk_count = int(metrics.get("chunk_count", 0))
        run.embed_seconds = float(metrics.get("embed_seconds", 0.0))
        run.total_seconds = float(metrics.get("total_seconds", 0.0))
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                "status",
                "chunk_count",
                "embed_seconds",
                "total_seconds",
                "finished_at",
                "updated_at",
            ]
        )
        logger.info(
            "task_metrics task_id=%s document_id=%s chunk_count=%s embed_seconds=%.3f total_seconds=%.3f",
            self.request.id,
            document_id,
            run.chunk_count,
            run.embed_seconds,
            run.total_seconds,
        )
        return {"document_id": document_id, "status": "COMPLETED"}
    except Exception as exc:  # noqa: BLE001
        run.retries = self.request.retries
        run.failure_reason = str(exc)
        if _is_recoverable_error(exc) and self.request.retries < self.max_retries:
            run.status = ProcessingRunModel.STATUS_RETRY
            run.save(update_fields=["status", "retries", "failure_reason", "updated_at"])
            logger.warning(
                "recoverable_error task_id=%s document_id=%s retry=%s reason=%s",
                self.request.id,
                document_id,
                self.request.retries + 1,
                exc,
            )
            raise self.retry(exc=exc, countdown=2 ** (self.request.retries + 1))

        run.status = ProcessingRunModel.STATUS_FAILED
        run.finished_at = timezone.now()
        run.save(
            update_fields=["status", "retries", "failure_reason", "finished_at", "updated_at"]
        )
        logger.exception(
            "non_recoverable_error task_id=%s document_id=%s retries=%s",
            self.request.id,
            document_id,
            self.request.retries,
        )
        raise
