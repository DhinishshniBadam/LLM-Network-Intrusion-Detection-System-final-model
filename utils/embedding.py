import numpy as np
from sentence_transformers import SentenceTransformer

_model = None

def get_bert_model():
    global _model
    if _model is None:
        # lightweight BERT model (~90MB), no GPU needed
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: list[str]) -> np.ndarray:
    """Return BERT embeddings for a list of payload text strings. Shape: (N, 384)"""
    model = get_bert_model()
    return model.encode(texts, batch_size=256, show_progress_bar=False)

def embed_single(text: str) -> np.ndarray:
    """Return BERT embedding for a single text string. Shape: (384,)"""
    return embed_texts([text])[0]
