from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from PIL import Image


ASSET_TYPES = {"image", "icon", "photo"}


def crop_visual_assets(
    scene: Dict[str, Any],
    image_path: str,
    out_dir: str,
    padding: int = 0,
) -> Dict[str, Any]:
    """Crop photo/icon assets from the original slide image.

    This preserves visual fidelity better than redrawing a meter/photo/icon from
    scratch. Existing explicit paths are respected.
    """
    src = Image.open(image_path).convert("RGBA")
    src_w, src_h = src.size
    sw, sh = scene.get("slide_size", [src_w, src_h])
    asset_dir = Path(out_dir)
    asset_dir.mkdir(parents=True, exist_ok=True)

    updated = {**scene, "objects": []}
    for obj in scene.get("objects", []):
        item = dict(obj)
        if item.get("type") in ASSET_TYPES and not item.get("path"):
            x, y, w, h = item["bbox"]
            left = max(0, int((x / sw) * src_w) - padding)
            top = max(0, int((y / sh) * src_h) - padding)
            right = min(src_w, int(((x + w) / sw) * src_w) + padding)
            bottom = min(src_h, int(((y + h) / sh) * src_h) + padding)
            if right > left and bottom > top:
                crop = src.crop((left, top, right, bottom))
                out = asset_dir / f"{item.get('id', 'asset')}.png"
                crop.save(out)
                item["type"] = "image"
                item["path"] = str(out)
                item["asset_strategy"] = "cropped_from_source"
        updated["objects"].append(item)

    return updated
