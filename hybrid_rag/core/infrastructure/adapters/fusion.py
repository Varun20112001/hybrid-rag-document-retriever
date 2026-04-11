from core.application.interfaces import FusionService


class RRFFusionService(FusionService):
    def fuse(self, lexical, semantic, k: int):
        merged = {}

        for rank, item in enumerate(lexical, start=1):
            key = str(item.chunk_id)
            item.scores.rrf_score += 1.0 / (k + rank)
            merged[key] = item

        for rank, item in enumerate(semantic, start=1):
            key = str(item.chunk_id)
            increment = 1.0 / (k + rank)
            if key in merged:
                merged[key].scores.rrf_score += increment
                merged[key].scores.vector_score = max(
                    merged[key].scores.vector_score, 
                    item.scores.vector_score
                )
            else:
                item.scores.rrf_score += increment
                merged[key] = item

        return sorted(merged.values(), key=lambda x: x.scores.rrf_score, reverse=True)
