import logging
import os
import threading

from sentence_transformers import CrossEncoder, SentenceTransformer

from core.infrastructure.runtime.settings import RuntimeSettings

logger = logging.getLogger(__name__)


class ModelRegistry:
    _lock = threading.Lock()
    _embedder = None
    _reranker = None
    _settings = RuntimeSettings.from_env()

    @classmethod
    def _configure_env(cls) -> None:
        if cls._settings.hf_home:
            os.environ.setdefault("HF_HOME", cls._settings.hf_home)
        if cls._settings.transformers_cache:
            os.environ.setdefault("TRANSFORMERS_CACHE", cls._settings.transformers_cache)
        if cls._settings.sentence_transformers_home:
            os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cls._settings.sentence_transformers_home)
        os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
        if cls._settings.hf_hub_offline:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")

    @classmethod
    def get_embedder(cls) -> SentenceTransformer:
        with cls._lock:
            if cls._embedder is None:
                cls._configure_env()
                cls._embedder = SentenceTransformer(
                    cls._settings.embedding_model,
                    device=cls._settings.embed_device,
                )
                cls._embedder.max_seq_length = cls._settings.embed_max_seq_length
                logger.info(
                    "Loaded embedding model: model=%s device=%s",
                    cls._settings.embedding_model,
                    cls._settings.embed_device or "auto",
                )
            return cls._embedder

    @classmethod
    def get_reranker(cls) -> CrossEncoder:
        with cls._lock:
            if cls._reranker is None:
                cls._configure_env()
                cls._reranker = CrossEncoder(
                    cls._settings.reranker_model,
                    device=cls._settings.embed_device,
                )
                logger.info(
                    "Loaded reranker model: model=%s device=%s",
                    cls._settings.reranker_model,
                    cls._settings.embed_device or "auto",
                )
            return cls._reranker

    @classmethod
    def warmup(cls, include_reranker: bool = True) -> None:
        cls.get_embedder()
        if include_reranker:
            cls.get_reranker()

    @classmethod
    def runtime_settings(cls) -> RuntimeSettings:
        return cls._settings
