from __future__ import annotations
from dataclasses import dataclass

@dataclass
class FitResult:
    font_size: float
    lines: int
    overflow: bool
    estimated_width: float
    estimated_height: float

def estimate_text_size(text: str, font_size: float, max_width: float, line_height: float = 1.35) -> FitResult:
    # Conservative CJK estimator. PowerPoint/QuickLook often wraps Chinese text
    # later than browser previews but uses taller line boxes, so keep height
    # pessimistic to block false "pass" results before visual review.
    width = 0.0
    lines = 1
    current = 0.0
    for ch in text:
        cw = font_size * (1.08 if '\u4e00' <= ch <= '\u9fff' else 0.58)
        if ch == "\n" or current + cw > max_width:
            lines += 1
            current = 0.0 if ch == "\n" else cw
        else:
            current += cw
        width = max(width, current)
    height = lines * font_size * line_height
    return FitResult(font_size, lines, False, width, height)

def fit_font_size(text: str, max_width: float, max_height: float, start: float, min_size: float = 8) -> FitResult:
    size = start
    while size >= min_size:
        r = estimate_text_size(text, size, max_width)
        r.overflow = r.estimated_height > max_height
        if not r.overflow:
            return r
        size -= 0.5
    r = estimate_text_size(text, min_size, max_width)
    r.overflow = True
    return r
