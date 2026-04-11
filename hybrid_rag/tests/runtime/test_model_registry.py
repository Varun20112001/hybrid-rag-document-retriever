from core.infrastructure.runtime.model_registry import ModelRegistry


def test_model_registry_is_singleton_within_process(monkeypatch):
    class DummyModel:
        max_seq_length = 0

    class DummyCross:
        pass

    monkeypatch.setattr("core.infrastructure.runtime.model_registry.SentenceTransformer", lambda *args, **kwargs: DummyModel())
    monkeypatch.setattr("core.infrastructure.runtime.model_registry.CrossEncoder", lambda *args, **kwargs: DummyCross())
    ModelRegistry._embedder = None
    ModelRegistry._reranker = None

    first = ModelRegistry.get_embedder()
    second = ModelRegistry.get_embedder()
    assert first is second

    r1 = ModelRegistry.get_reranker()
    r2 = ModelRegistry.get_reranker()
    assert r1 is r2
