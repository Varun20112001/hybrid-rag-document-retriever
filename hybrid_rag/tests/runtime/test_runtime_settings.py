from core.infrastructure.runtime.settings import RuntimeSettings


def test_runtime_settings_defaults(monkeypatch):
    monkeypatch.delenv("EMBED_BATCH_SIZE", raising=False)
    cfg = RuntimeSettings.from_env()
    assert cfg.embed_batch_size == 32


def test_runtime_settings_clamps_batch_size(monkeypatch):
    monkeypatch.setenv("EMBED_BATCH_SIZE", "9999")
    cfg = RuntimeSettings.from_env()
    assert cfg.embed_batch_size == 256
