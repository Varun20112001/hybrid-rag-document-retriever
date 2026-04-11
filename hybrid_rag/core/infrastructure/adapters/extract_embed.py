import os
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from core.application.interfaces import EmbeddingService, TextExtractor


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
    def __init__(self, model_name: str | None = None):
        model = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    def embed_query(self, query: str) -> list[float]:
        return self.embed([query])[0]
