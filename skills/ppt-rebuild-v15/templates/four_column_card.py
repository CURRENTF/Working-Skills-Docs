from __future__ import annotations
from typing import Dict, Any

def build_plan(scene: Dict[str, Any]) -> Dict[str, Any]:
    return {'template_id': 'four_column_card', 'placements': [], 'constraints': ['uniform card grid'], 'qa_hints': {'regions':['cards']}}
