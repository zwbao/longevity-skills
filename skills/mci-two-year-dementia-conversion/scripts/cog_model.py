"""Standard-library evaluation of the exported cognitive-scores model.

The published pipeline, for a row with all six scores present, is:
KNN imputer (a no-op when nothing is missing), variance and correlation
filters (both keep all six columns in every fold), XGBoost, then per fold
sigmoid calibration ``1 / (1 + exp(a * p + b))`` on the XGBoost probability
``p``; scikit-learn's CalibratedClassifierCV averages the five calibrated
probabilities. SMOTENC only acts during fitting.

XGBoost compares float32 inputs with float32 split values and goes left when
``x < split``; the inputs and splits are rounded to float32 the same way here.
"""

from __future__ import annotations

import json
import math
import struct
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Sequence

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "cog_model.json"


def _f32(value: float) -> float:
    return struct.unpack("f", struct.pack("f", value))[0]


@lru_cache(maxsize=1)
def load_model() -> Dict:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    for fold in model["folds"]:
        for tree in fold["trees"]:
            tree[1] = [_f32(v) for v in tree[1]]
    return model


def _tree_value(tree: Sequence[List], x: Sequence[float]) -> float:
    split_index, split_value, left, right, _default_left = tree
    node = 0
    while left[node] != -1:
        node = left[node] if x[split_index[node]] < split_value[node] else right[node]
    return split_value[node]


def fold_probabilities(values: Sequence[float]) -> List[float]:
    """Calibrated probability of two-year conversion from each of the five folds."""
    model = load_model()
    if len(values) != len(model["features"]):
        raise ValueError(f"expected {len(model['features'])} scores, got {len(values)}")
    x = [_f32(float(v)) for v in values]
    out = []
    for fold in model["folds"]:
        base = fold["base_score"]
        margin = math.log(base / (1.0 - base)) + sum(_tree_value(t, x) for t in fold["trees"])
        p = 1.0 / (1.0 + math.exp(-margin))
        out.append(1.0 / (1.0 + math.exp(fold["sigmoid_a"] * p + fold["sigmoid_b"])))
    return out


def conversion_probability(values: Sequence[float]) -> float:
    """Mean of the five calibrated probabilities, as CalibratedClassifierCV.predict_proba."""
    folds = fold_probabilities(values)
    return sum(folds) / len(folds)


def threshold() -> float:
    return float(load_model()["threshold"])
