from __future__ import annotations
from typing import List, Dict, Any
from layout.layout_solver import rects_overlap

def audit_overlap(elements: List[Dict[str, Any]], threshold: float = 0.03) -> Dict[str, Any]:
    issues = []
    for i, a in enumerate(elements):
        for j, b in enumerate(elements[i+1:], start=i+1):
            if a.get('allow_overlap') or b.get('allow_overlap'):
                continue
            r = rects_overlap(a['bbox'], b['bbox'])
            if r > threshold:
                issues.append({'a': a.get('id'), 'b': b.get('id'), 'ratio': r})
    return {'status': 'pass' if not issues else 'fail', 'issues': issues}
