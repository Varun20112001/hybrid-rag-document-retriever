from celery import shared_task

from core.infrastructure.services.container import build_process_use_case


@shared_task(
    bind=True, autoretry_for=(Exception,), 
    retry_backoff=True, retry_kwargs={"max_retries": 3}
)
def process_document_task(self, document_id: str):
    use_case = build_process_use_case()
    use_case.execute(document_id)
    return {"document_id": document_id, "status": "COMPLETED"}
