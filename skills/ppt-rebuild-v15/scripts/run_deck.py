from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from classify.template_router import route
from extract.asset_generate import generate_missing_visual_assets
from qa.audit_overlap import audit_overlap
from qa.audit_text_overflow import audit_text_overflow
from render.build_pptx import build_from_plans
from scripts.run_pipeline import _scene_texts, _text_value, build_scene_plan, build_textless_backdrop_plan


def _prepare_scene(scene: Dict[str, Any], image_path: str | None, out_dir: Path) -> Dict[str, Any]:
    if image_path:
        from extract.asset_crop import crop_visual_assets

        scene = crop_visual_assets(scene, image_path, str(out_dir / "assets" / "crops"), padding=0)
    return generate_missing_visual_assets(scene, str(out_dir / "assets" / "generated"))


def _plan_for_scene(scene: Dict[str, Any], image_path: str | None, slide_dir: Path, mode: str) -> tuple[Dict[str, Any], str, Dict[str, Any]]:
    r = route(scene)
    if mode in {"auto", "backdrop"} and image_path:
        return build_textless_backdrop_plan(scene, image_path, slide_dir / "assets"), "backdrop", r

    try:
        module = importlib.import_module(r["template_module"])
        candidate = module.build_plan(scene)
    except Exception:
        candidate = {}
    return candidate if candidate.get("placements") else build_scene_plan(scene), "scene", r


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenes", nargs="+", required=True)
    parser.add_argument("--images", nargs="*", help="Original source images, one per scene.")
    parser.add_argument("--mode", choices=["auto", "backdrop", "scene"], default="scene")
    parser.add_argument("--out", required=True)
    parser.add_argument("--plans-out")
    args = parser.parse_args()

    images = args.images or []
    if images and len(images) != len(args.scenes):
        raise SystemExit("--images must contain exactly one image path per scene.")

    out_path = Path(args.out)
    plans: List[Dict[str, Any]] = []
    qa_slides: List[Dict[str, Any]] = []

    for idx, scene_file in enumerate(args.scenes, start=1):
        image_path = images[idx - 1] if images else None
        slide_dir = out_path.with_suffix("").parent / f"slide_{idx:02d}"
        scene = json.load(open(scene_file, "r", encoding="utf-8"))
        scene = _prepare_scene(scene, image_path, slide_dir)
        plan, selected_mode, r = _plan_for_scene(scene, image_path, slide_dir, args.mode)
        plans.append(plan)
        texts = _scene_texts(scene)
        qa_slides.append(
            {
                "scene": scene_file,
                "source_image": image_path,
                "mode": selected_mode,
                "route": r,
                "editable_text_count": len(texts),
                "editable_char_count": sum(len(_text_value(t)) for t in texts),
                "overflow": audit_text_overflow(texts),
                "overlap": audit_overlap([obj for obj in texts if "bbox" in obj]),
                "plan_template_id": plan.get("template_id"),
                "placement_count": len(plan.get("placements", [])),
            }
        )

    build_from_plans(plans, args.out)
    qa = {
        "version": "v15",
        "slide_count": len(plans),
        "mode": args.mode,
        "slides": qa_slides,
        "status": "pass"
        if all(s["overflow"]["status"] == "pass" and s["overlap"]["status"] == "pass" for s in qa_slides)
        else "review",
    }
    qa_path = out_path.with_suffix(".qa.json")
    json.dump(qa, open(qa_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if args.plans_out:
        json.dump(plans, open(args.plans_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"pptx": args.out, "qa": str(qa_path), "slide_count": len(plans), "status": qa["status"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
