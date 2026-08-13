import numpy as np
from typing import List, Dict, Any

class MemoryStore:
    def __init__(self):
        self.memories = []
        self.embeddings = []

    def _get_embedding(self, text: str) -> np.ndarray:
        # Mock embedding from BGE-M3
        np.random.seed(hash(text) % (2**32))
        vec = np.random.randn(768)
        return vec / np.linalg.norm(vec)

    def add_memory(self, memory_id: str, text: str, memory_type: str, month: int):
        embedding = self._get_embedding(text)
        self.memories.append({
            "id": memory_id,
            "text": text,
            "type": memory_type,
            "month": month
        })
        self.embeddings.append(embedding)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.embeddings:
            return []
            
        query_emb = self._get_embedding(query)
        embeddings_matrix = np.vstack(self.embeddings)
        
        # Cosine similarity
        similarities = np.dot(embeddings_matrix, query_emb)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [self.memories[idx] for idx in top_indices]
        return results
