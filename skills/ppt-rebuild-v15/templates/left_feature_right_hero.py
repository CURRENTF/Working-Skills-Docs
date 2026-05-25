from __future__ import annotations
from typing import Dict, Any

def build_plan(scene: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'template_id': 'left_feature_right_hero',
        'placements': [],
        'constraints': [
            'left intro cannot overlap feature cards',
            'feature cards have consistent height and icon/title/body columns',
            'right hero image is contain-fitted inside bordered card',
            'bottom metrics are centered and non-overlapping',
        ],
        'qa_hints': {'regions': ['header','progress','left_features','hero','bottom_metrics']}
    }
