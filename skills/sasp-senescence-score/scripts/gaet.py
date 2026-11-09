"""NumPy forward pass of the GAET encoder and guidance head (SASP Score).

Mirrors TGAE.predict in shangshuzhao/sasp (tgae.py, commit 34d5f1b): protein
name embedding + value embedding, two post-norm TransformerEncoder layers
(8 heads, d_model 128, feed-forward 2048, ReLU, LayerNorm eps 1e-5, dropout
off at inference), mean pooling over proteins, latent_proj (128 -> 6) and the
regressor (6 -> 1). The decoder only reconstructs inputs and is not needed for
the score. Weights are the authors' tgae_pre_trained.pth, frozen to
data/gaet_pretrained_encoder.npz (float32, unchanged values).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

import numpy as np

from presets import N_HEADS, N_LAYERS, PROTEINS, WEIGHTS_FILE, LAYER_NORM_EPS

_CACHE: Dict[str, np.ndarray] = {}


def load_weights(path: Path = WEIGHTS_FILE) -> Dict[str, np.ndarray]:
    if not _CACHE:
        with np.load(path) as data:
            for key in data.files:
                _CACHE[key.replace("__", ".")] = data[key].astype(np.float64)
    return _CACHE


def _layer_norm(x: np.ndarray, weight: np.ndarray, bias: np.ndarray) -> np.ndarray:
    mean = x.mean(axis=-1, keepdims=True)
    var = x.var(axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + LAYER_NORM_EPS) * weight + bias


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)


def _encoder_layer(h: np.ndarray, w: Dict[str, np.ndarray], prefix: str) -> np.ndarray:
    p, d = h.shape
    head = d // N_HEADS
    qkv = h @ w[prefix + "self_attn.in_proj_weight"].T + w[prefix + "self_attn.in_proj_bias"]
    q, k, v = qkv[:, :d], qkv[:, d:2 * d], qkv[:, 2 * d:]
    q = q.reshape(p, N_HEADS, head).transpose(1, 0, 2)
    k = k.reshape(p, N_HEADS, head).transpose(1, 0, 2)
    v = v.reshape(p, N_HEADS, head).transpose(1, 0, 2)
    attn = _softmax(q @ k.transpose(0, 2, 1) / np.sqrt(head)) @ v
    attn = attn.transpose(1, 0, 2).reshape(p, d)
    attn = attn @ w[prefix + "self_attn.out_proj.weight"].T + w[prefix + "self_attn.out_proj.bias"]
    h = _layer_norm(h + attn, w[prefix + "norm1.weight"], w[prefix + "norm1.bias"])
    ff = np.maximum(h @ w[prefix + "linear1.weight"].T + w[prefix + "linear1.bias"], 0.0)
    ff = ff @ w[prefix + "linear2.weight"].T + w[prefix + "linear2.bias"]
    return _layer_norm(h + ff, w[prefix + "norm2.weight"], w[prefix + "norm2.bias"])


def sasp_score(values: Sequence[float], proteins: Sequence[str] = PROTEINS) -> float:
    """SASP Score for one sample. ``values`` are NPX values aligned to ``proteins``."""
    w = load_weights()
    idx = [PROTEINS.index(name) for name in proteins]
    x = np.asarray(values, dtype=np.float64)
    if x.shape != (len(idx),) or not np.all(np.isfinite(x)):
        raise ValueError("values must be finite and match proteins")
    h = w["encoder.var_name_embedding.weight"][idx]
    h = h + x[:, None] * w["encoder.var_value_embedding.weight"][:, 0] + w["encoder.var_value_embedding.bias"]
    for layer in range(N_LAYERS):
        h = _encoder_layer(h, w, f"encoder.transformer_encoder.layers.{layer}.")
    pooled = h.mean(axis=0)
    latent = pooled @ w["latent_proj.weight"].T + w["latent_proj.bias"]
    return float((latent @ w["regressor.weight"].T + w["regressor.bias"])[0])
