from sentence_transformers import CrossEncoder

from core.application.interfaces import RerankerService
from core.infrastructure.runtime.model_registry import ModelRegistry


class CrossEncoderReranker(RerankerService):
    def __init__(self, model: CrossEncoder | None = None):
        self.model = model or ModelRegistry.get_reranker()

    def rerank(self, query: str, results: list, top_k: int):
        if not results:
            return []
        pairs = [[query, item.text] for item in results]
        scores = self.model.predict(pairs)
        for item, score in zip(results, scores):
            item.scores.rerank_score = float(score)
        return sorted(results, key=lambda item: item.scores.rerank_score, reverse=True)[:top_k]
