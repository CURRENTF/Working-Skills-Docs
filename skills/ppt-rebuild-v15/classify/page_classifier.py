from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class PagePrediction:
    page_type: str
    confidence: float
    reasons: List[str]

KNOWN_TYPES = {
    "three_card_energy",
    "left_feature_right_hero",
    "left_argument_arrow_infographic",
    "four_column_card",
    "paradigm_shift_1_vs_2",
    "textless_backdrop_editable_layer",
    "editable_scene",
}

def classify_scene(scene: Dict[str, Any]) -> PagePrediction:
    explicit = scene.get("page_type")
    if explicit in KNOWN_TYPES:
        return PagePrediction(explicit, 0.99, ["explicit page_type in scene graph"])
    """Heuristic classifier over VLM/OCR scene graph.

    This is intentionally deterministic. A production build can replace this
    with VLM classification but should keep this as a safety fallback.
    """
    objects = scene.get("objects", [])
    texts = [o.get("text", "") for o in objects if o.get("type") == "text"]
    joined = " ".join(texts)
    image_count = sum(1 for o in objects if o.get("type") == "image")
    card_count = sum(1 for o in objects if o.get("type") in {"card", "group"})
    reasons = []

    if "绿色能源" in joined and ("光伏" in joined or "储能" in joined) and image_count >= 3:
        reasons.append("green-energy keywords and >=3 images")
        return PagePrediction("three_card_energy", 0.88, reasons)
    if "监测计量" in joined and ("数据可信" in joined or "雷达遥感" in joined) and image_count >= 1:
        reasons.append("monitoring keywords with hero image")
        return PagePrediction("left_feature_right_hero", 0.86, reasons)
    if "市场洞察" in joined and ("欧美" in joined or "链主" in joined) and ("万亿" in joined or "双碳市场" in joined):
        reasons.append("market insight arrow infographic keywords")
        return PagePrediction("left_argument_arrow_infographic", 0.87, reasons)
    if "跨越拐点" in joined and ("1.0" in joined and "2.0" in joined) and "范式革新" in joined:
        reasons.append("paradigm shift comparison keywords")
        return PagePrediction("paradigm_shift_1_vs_2", 0.9, reasons)
    if card_count >= 4 and image_count >= 4:
        reasons.append("four or more cards/images")
        return PagePrediction("four_column_card", 0.72, reasons)
    reasons.append("unknown structured page; fallback to textless backdrop")
    return PagePrediction("textless_backdrop_editable_layer", 0.45, reasons)
