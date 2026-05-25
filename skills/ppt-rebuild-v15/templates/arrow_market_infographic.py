from __future__ import annotations
from typing import Dict, Any

def build_plan(scene: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'template_id': 'left_argument_arrow_infographic',
        'placements': [],
        'constraints': [
            'left argument cards use fixed 3-row grid',
            'right lanes are arrow infographic grammar, not free-form shapes',
            'target arrow label must be vertically centered',
            'three KPI blocks must have minimum gap and independent text boxes',
        ],
        'qa_hints': {'regions': ['left_cards','arrow_infographic','emphasis_bar','kpis','conclusion']}
    }
