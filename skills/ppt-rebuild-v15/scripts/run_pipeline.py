from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from classify.template_router import route
from qa.audit_overlap import audit_overlap
from qa.audit_text_overflow import audit_text_overflow
from render.build_pptx import build_from_plan


def _scene_texts(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [o for o in scene.get("objects", []) if o.get("type") in {"text", "rich_text"}]


def _text_value(obj: Dict[str, Any]) -> str:
    if obj.get("type") == "rich_text":
        return "".join(segment.get("text", "") for segment in obj.get("segments", []))
    return obj.get("text", "")


def build_textless_backdrop_plan(scene: Dict[str, Any], image_path: str, work_dir: Path) -> Dict[str, Any]:
    from extract.text_inpaint import create_textless_backdrop

    work_dir.mkdir(parents=True, exist_ok=True)
    backdrop = work_dir / "textless_backdrop.png"
    create_textless_backdrop(image_path, scene, str(backdrop))
    slide_size = scene.get("slide_size", [1600, 900])
    placements: List[Dict[str, Any]] = [
        {"id": "textless_backdrop", "type": "image", "path": str(backdrop), "bbox": [0, 0, slide_size[0], slide_size[1]], "z": 0}
    ]
    for idx, text in enumerate(_scene_texts(scene), start=1):
        placements.append({**text, "type": "text", "z": 10 + idx})
    return {
        "template_id": "textless_backdrop_editable_layer",
        "slide_size": slide_size,
        "placements": placements,
        "source_image": image_path,
        "asset_base_dir": str(Path(__file__).resolve().parents[1]),
    }


def build_scene_plan(scene: Dict[str, Any]) -> Dict[str, Any]:
    placements: List[Dict[str, Any]] = []
    for idx, obj in enumerate(scene.get("objects", []), start=1):
        item = dict(obj)
        item.setdefault("z", idx)
        if item.get("type") == "card":
            item["type"] = "rounded_rect"
            item.setdefault("shape", "rounded_rect")
        placements.append(item)
    return {
        "template_id": scene.get("page_type", "editable_scene"),
        "slide_size": scene.get("slide_size", [1600, 900]),
        "placements": placements,
        "asset_base_dir": str(Path(__file__).resolve().parents[1]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, help="Scene graph JSON. OCR/VLM extraction should produce this file.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--image", help="Original slide image. When supplied, v15 uses textless backdrop + editable text by default.")
    ap.add_argument("--mode", choices=["auto", "backdrop", "scene"], default="auto")
    ap.add_argument("--plan-out")
    args = ap.parse_args()

    scene_path = Path(args.scene)
    scene = json.load(open(scene_path, "r", encoding="utf-8"))
    if args.image:
        from extract.asset_crop import crop_visual_assets

        scene = crop_visual_assets(
            scene,
            args.image,
            str(Path(args.out).with_suffix("").parent / "assets" / "crops"),
            padding=0,
        )
    from extract.asset_generate import generate_missing_visual_assets

    scene = generate_missing_visual_assets(
        scene,
        str(Path(args.out).with_suffix("").parent / "assets" / "generated"),
    )
    r = route(scene)

    if args.mode in {"auto", "backdrop"} and args.image:
        plan = build_textless_backdrop_plan(scene, args.image, Path(args.out).with_suffix("").parent / "assets")
        selected_mode = "backdrop"
    else:
        # The routed template is still reported, but v15 does not trust empty
        # template plans. Use the editable scene plan unless a future template
        # returns real placements.
        selected_mode = "scene"
        try:
            module = importlib.import_module(r["template_module"])
            candidate = module.build_plan(scene)
        except Exception:
            candidate = {}
        plan = candidate if candidate.get("placements") else build_scene_plan(scene)

    build_from_plan(plan, args.out)
    texts = _scene_texts(scene)
    qa = {
        "version": "v15",
        "mode": selected_mode,
        "route": r,
        "editable_text_count": len(texts),
        "editable_char_count": sum(len(_text_value(t)) for t in texts),
        "overflow": audit_text_overflow(texts),
        "overlap": audit_overlap([obj for obj in texts if "bbox" in obj]),
        "plan_template_id": plan.get("template_id"),
        "placement_count": len(plan.get("placements", [])),
    }
    report_path = Path(args.out).with_suffix(".qa.json")
    json.dump(qa, open(report_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if args.plan_out:
        json.dump(plan, open(args.plan_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"pptx": args.out, "qa": str(report_path), "mode": selected_mode, "route": r}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
