import numpy as np

def fuse(semantic: np.ndarray, structural: np.ndarray) -> np.ndarray:
    """
    Concatenate BERT semantic embeddings with structural features.
    semantic:   (N, 384)
    structural: (N, 38)
    returns:    (N, 422)
    """
    return np.concatenate([semantic, structural], axis=1)

def fuse_single(semantic: np.ndarray, structural: np.ndarray) -> np.ndarray:
    """Fuse a single sample. Returns shape (1, 422) for LSTM input."""
    combined = np.concatenate([semantic, structural])
    return combined.reshape(1, 1, -1)  # (batch=1, timesteps=1, features=422)
