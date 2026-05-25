from __future__ import annotations
from typing import Dict, Any

def build_plan(scene: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'template_id': 'three_card_energy',
        'placements': [],
        'constraints': [
            'three equal cards with fixed top image window',
            'title strip must not overlap bullets',
            'bottom metric strip must be separate from timeline',
        ],
        'qa_hints': {'regions': ['header','subtitle','cards','metrics','timeline']}
    }
