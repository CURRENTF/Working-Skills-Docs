from __future__ import annotations
from typing import List, Dict, Any

def rects_overlap(a, b) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0, min(ax+aw, bx+bw) - max(ax, bx))
    iy = max(0, min(ay+ah, by+bh) - max(ay, by))
    inter = ix * iy
    if inter == 0:
        return 0.0
    return inter / max(1e-6, min(aw*ah, bw*bh))

def solve_basic_constraints(elements: List[Dict[str, Any]], min_gap: float = 6.0) -> List[Dict[str, Any]]:
    # conservative vertical nudging for text objects inside the same container.
    out = [dict(e) for e in elements]
    for i in range(len(out)):
        for j in range(i+1, len(out)):
            if rects_overlap(out[i]['bbox'], out[j]['bbox']) > 0:
                x,y,w,h = out[j]['bbox']
                out[j]['bbox'] = [x, y + min_gap, w, h]
    return out
