from __future__ import annotations
from typing import List, Dict, Any
from layout.fit_text import fit_font_size

def audit_text_overflow(texts: List[Dict[str, Any]]) -> Dict[str, Any]:
    issues=[]
    for t in texts:
        x,y,w,h=t['bbox']
        start=t.get('style',{}).get('font_size',16)
        r=fit_font_size(t.get('text',''), w, h, start)
        if r.overflow:
            issues.append({'id':t.get('id'), 'text':t.get('text','')[:30], 'bbox':t['bbox']})
    return {'status':'pass' if not issues else 'fail', 'issues': issues}
