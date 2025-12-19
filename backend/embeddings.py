import os
from dotenv import load_dotenv
import logging
from typing import List

import google.generativeai as genai

logger = logging.getLogger(__name__)
load_dotenv()

# Configure the Gemini API client with your key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class GeminiEmbeddings:
    def __init__(self):
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment")

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for single text using Gemini Embedding model."""
        try:
            result = genai.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )
            # The API returns a list of vectors
            return result.embeddings
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # fallback simple embedding
            return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> List[float]:
        """Fallback embedding if API fails"""
        import hashlib
        text_hash = hashlib.sha256(text.encode()).digest()
        vector = [float((b % 100) / 100.0) for b in text_hash]
        while len(vector) < 384:
            vector.extend(vector[:min(384 - len(vector), len(vector))])
        return vector[:384]

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings"""
        embeddings = []
        for text in texts:
            emb = await self.get_embedding(text)
            embeddings.append(emb)
        return embeddings
