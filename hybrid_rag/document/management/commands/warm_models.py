from django.core.management.base import BaseCommand

from core.infrastructure.runtime.model_registry import ModelRegistry


class Command(BaseCommand):
    help = "Preload embedding and reranker models into local cache."

    def handle(self, *args, **options):
        ModelRegistry.warmup(include_reranker=True)
        settings = ModelRegistry.runtime_settings()
        self.stdout.write(
            self.style.SUCCESS(
                "Models warmed: "
                f"embedding={settings.embedding_model} reranker={settings.reranker_model}"
            )
        )
