from __future__ import annotations
from typing import Dict, Any
from classify.page_classifier import classify_scene

TEMPLATE_MAP = {
    "three_card_energy": "templates.three_card_energy",
    "left_feature_right_hero": "templates.left_feature_right_hero",
    "left_argument_arrow_infographic": "templates.arrow_market_infographic",
    "four_column_card": "templates.four_column_card",
    "paradigm_shift_1_vs_2": "templates.textless_backdrop",
    "textless_backdrop_editable_layer": "templates.textless_backdrop",
    "editable_scene": "templates.textless_backdrop",
}

def route(scene: Dict[str, Any]) -> Dict[str, Any]:
    predicted = classify_scene(scene)
    return {
        "page_type": predicted.page_type,
        "template_module": TEMPLATE_MAP[predicted.page_type],
        "confidence": predicted.confidence,
        "reasons": predicted.reasons,
    }
