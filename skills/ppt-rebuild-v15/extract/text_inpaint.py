from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

import cv2
import numpy as np


def text_objects(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [obj for obj in scene.get("objects", []) if obj.get("type") in {"text", "rich_text"}]


def build_text_mask(image_shape: tuple[int, int, int], scene: Dict[str, Any], padding: int = 8) -> np.ndarray:
    height, width = image_shape[:2]
    sw, sh = scene.get("slide_size", [width, height])
    mask = np.zeros((height, width), dtype=np.uint8)

    for obj in text_objects(scene):
        x, y, w, h = obj["bbox"]
        x1 = int(max(0, (x / sw) * width - padding))
        y1 = int(max(0, (y / sh) * height - padding))
        x2 = int(min(width, ((x + w) / sw) * width + padding))
        y2 = int(min(height, ((y + h) / sh) * height + padding))
        if x2 > x1 and y2 > y1:
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

    return mask


def create_textless_backdrop(
    image_path: str,
    scene: Dict[str, Any],
    out_path: str,
    padding: int = 8,
    radius: int = 3,
) -> str:
    """Remove detected text regions from a slide image using OpenCV inpainting.

    The scene graph supplies text bboxes. This is intentionally deterministic:
    OCR/VLM can improve the scene, but this step should never invent layout.
    """
    source = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if source is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    mask = build_text_mask(source.shape, scene, padding=padding)
    if int(np.count_nonzero(mask)) == 0:
        result = source
    else:
        result = cv2.inpaint(source, mask, radius, cv2.INPAINT_TELEA)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(out), result):
        raise RuntimeError(f"Failed to write textless backdrop: {out}")
    return str(out)
