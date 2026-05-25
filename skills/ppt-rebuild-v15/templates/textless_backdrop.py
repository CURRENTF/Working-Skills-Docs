from __future__ import annotations
from typing import Dict, Any

def build_plan(scene: Dict[str, Any]) -> Dict[str, Any]:
    return {'template_id': 'textless_backdrop_editable_layer', 'placements': [], 'constraints': ['backdrop must pass no-text audit'], 'qa_hints': {'regions':['backdrop','editable_texts']}}
