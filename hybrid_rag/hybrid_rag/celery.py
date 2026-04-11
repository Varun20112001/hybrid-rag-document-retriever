from celery import Celery
from celery.signals import worker_process_init

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hybrid_rag.settings")

app = Celery("hybrid_rag")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_process_init.connect
def preload_models(**kwargs):  # noqa: ARG001
    from core.infrastructure.runtime.model_registry import ModelRegistry

    ModelRegistry.warmup(include_reranker=True)
