from dataclasses import dataclass
import os


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _clamp_int(value: str | None, default: int, low: int, high: int) -> int:
    try:
        parsed = int(value) if value is not None else default
    except ValueError:
        parsed = default
    return max(low, min(high, parsed))


@dataclass(frozen=True)
class RuntimeSettings:
    embedding_model: str
    reranker_model: str
    embed_device: str | None
    embed_batch_size: int
    embed_normalize: bool
    embed_show_progress_bar: bool
    embed_max_seq_length: int
    hf_home: str | None
    transformers_cache: str | None
    sentence_transformers_home: str | None
    hf_hub_offline: bool

    @classmethod
    def from_env(cls) -> "RuntimeSettings":
        return cls(
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            reranker_model=os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
            embed_device=os.getenv("EMBED_DEVICE"),
            embed_batch_size=_clamp_int(os.getenv("EMBED_BATCH_SIZE"), default=32, low=1, high=256),
            embed_normalize=_to_bool(os.getenv("EMBED_NORMALIZE"), True),
            embed_show_progress_bar=_to_bool(os.getenv("EMBED_SHOW_PROGRESS_BAR"), False),
            embed_max_seq_length=_clamp_int(os.getenv("EMBED_MAX_SEQ_LENGTH"), default=512, low=64, high=4096),
            hf_home=os.getenv("HF_HOME"),
            transformers_cache=os.getenv("TRANSFORMERS_CACHE"),
            sentence_transformers_home=os.getenv("SENTENCE_TRANSFORMERS_HOME"),
            hf_hub_offline=_to_bool(os.getenv("HF_HUB_OFFLINE"), False),
        )
