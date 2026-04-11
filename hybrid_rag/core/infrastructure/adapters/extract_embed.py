from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from core.application.interfaces import EmbeddingService, TextExtractor
from core.infrastructure.runtime.model_registry import ModelRegistry


class FileTextExtractor(TextExtractor):
    def extract(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        if suffix == ".docx":
            doc = DocxDocument(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        if suffix in {".txt", ".md"}:
            return Path(file_path).read_text(encoding="utf-8", errors="ignore")
        raise ValueError(f"Unsupported file extension: {suffix}")


class HybridEmbeddingService(EmbeddingService):
    def __init__(self, model: SentenceTransformer | None = None):
        self.model = model or ModelRegistry.get_embedder()
        self.batch_size = ModelRegistry.runtime_settings().embed_batch_size
        self.normalize = ModelRegistry.runtime_settings().embed_normalize
        self.show_progress = ModelRegistry.runtime_settings().embed_show_progress_bar

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=self.show_progress,
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, query: str) -> list[float]:
        return self.embed([query])[0]
