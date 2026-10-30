import logging
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

try:
    import spaces
except ImportError:
    # Dummy decorator for local dev
    class spaces:
        @staticmethod
        def GPU(*args, **kwargs):
            def decorator(func):
                return func
            if len(args) == 1 and callable(args[0]):
                return args[0]
            return decorator

class RerankerService:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        
    @spaces.GPU(duration=60)
    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        if not chunks:
            return []
            
        if self.model is None:
            logger.info(f"Loading reranker model: {self.model_name}")
            self.model = CrossEncoder(self.model_name, max_length=512)
            
        # Prepare inputs: list of (query, document) pairs
        pairs = [[query, chunk["document"]] for chunk in chunks]
        
        try:
            from app.core.config import settings
            batch_size = getattr(settings, "RERANK_BATCH_SIZE", 32)
            scores = self.model.predict(pairs, batch_size=batch_size)
            import math
            # Attach scores and sort
            for i, chunk in enumerate(chunks):
                logit = float(scores[i])
                chunk["metadata"]["reranker_score"] = logit
                chunk["metadata"]["final_score"] = 1.0 / (1.0 + math.exp(-logit))
                
            # Sort by descending score
            ranked_chunks = sorted(chunks, key=lambda x: x["metadata"]["reranker_score"], reverse=True)
            
            return ranked_chunks[:top_k]
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return chunks[:top_k]

reranker_service = RerankerService()
