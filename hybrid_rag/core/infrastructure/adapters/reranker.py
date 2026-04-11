import os

from sentence_transformers import CrossEncoder

from core.application.interfaces import RerankerService


class CrossEncoderReranker(RerankerService):
    def __init__(self, model_name: str | None = None):
        model = model_name or os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.model = CrossEncoder(model)

    def rerank(self, query: str, results: list, top_k: int):
        if not results:
            return []
        pairs = [[query, item.text] for item in results]
        scores = self.model.predict(pairs)
        for item, score in zip(results, scores):
            item.scores.rerank_score = float(score)
        return sorted(results, key=lambda item: item.scores.rerank_score, reverse=True)[:top_k]
