from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import fitz


PROTECTED_TERMS = (
    "DeepSeek-V4",
    "DeepSeek-V4-Pro",
    "DeepSeek-V4-Flash",
    "DeepSeek-V4-Pro-Max",
    "DeepSeek-V3",
    "DeepSeek-V3.2",
    "DeepSeek Sparse Attention",
    "Compressed Sparse Attention",
    "Heavily Compressed Attention",
    "Manifold-Constrained Hyper-Connections",
    "Mixture-of-Experts",
    "MoE",
    "MLA",
    "CSA",
    "HCA",
    "DSA",
    "MTP",
    "FP4",
    "RL",
    "API",
    "KV",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare paragraph-level PDF annotation translation chunks and build an annotated PDF."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Extract paragraph blocks with coordinates.")
    prepare.add_argument("input_pdf", type=Path)
    prepare.add_argument("work_dir", type=Path)
    prepare.add_argument("--chunks", type=int, default=8)
    prepare.add_argument(
        "--min-chars",
        type=int,
        default=18,
        help="Skip shorter text blocks unless they look like headings. Default: 18.",
    )

    status = subparsers.add_parser("status", help="Report translation completion status.")
    status.add_argument("work_dir", type=Path)

    build = subparsers.add_parser("build", help="Copy the source PDF and add Chinese translation annotations.")
    build.add_argument("work_dir", type=Path)
    build.add_argument("output_pdf", type=Path)
    build.add_argument("--highlight", action="store_true", help="Also add translucent highlights over annotated blocks.")
    build.add_argument("--opacity", type=float, default=0.12, help="Highlight opacity. Default: 0.12.")
    build.add_argument(
        "--comment-mode",
        choices=("text", "highlight", "both"),
        default="both",
        help="Store comments in sticky-note text annotations, highlight annotations, or both. Default: both.",
    )

    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\x00", "")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:?!%)\]])", r"\1", text)
    text = re.sub(r"([([（])\s+", r"\1", text)
    return text.strip()


def looks_like_heading(text: str) -> bool:
    if len(text) > 110:
        return False
    if re.match(r"^\d+(\.\d+)*\.?\s+\S+", text):
        return True
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    if not words:
        return False
    titled = sum(1 for word in words if word[:1].isupper())
    return titled >= max(1, len(words) // 2)


def should_annotate(text: str, min_chars: int) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if re.fullmatch(r"\d+", stripped):
        return False
    if len(stripped) < min_chars and not looks_like_heading(stripped):
        return False
    letters = len(re.findall(r"[A-Za-z]", stripped))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", stripped))
    if letters + cjk < 3 and not looks_like_heading(stripped):
        return False
    return True


def text_blocks(page: fitz.Page, min_chars: int) -> list[dict[str, Any]]:
    blocks = []
    for raw in page.get_text("blocks", sort=True):
        x0, y0, x1, y1, raw_text, block_no, block_type = raw[:7]
        if block_type != 0:
            continue
        text = normalize_text(raw_text)
        if not should_annotate(text, min_chars):
            continue
        rect = fitz.Rect(x0, y0, x1, y1)
        if rect.is_empty or rect.width < 8 or rect.height < 6:
            continue
        blocks.append(
            {
                "block_no": int(block_no),
                "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                "text": text,
                "kind": "heading" if looks_like_heading(text) else "paragraph",
            }
        )
    return blocks


def prepare(input_pdf: Path, work_dir: Path, chunk_count: int, min_chars: int) -> None:
    if chunk_count < 1:
        raise ValueError("--chunks must be at least 1")
    if not input_pdf.exists():
        raise FileNotFoundError(input_pdf)

    doc = fitz.open(input_pdf)
    pages: list[list[dict[str, Any]]] = []
    flat_blocks: list[dict[str, Any]] = []
    next_id = 0
    for page_index, page in enumerate(doc):
        page_blocks: list[dict[str, Any]] = []
        for block in text_blocks(page, min_chars):
            item = {
                "id": f"a{next_id:05d}",
                "page": page_index + 1,
                "page_index": page_index,
                **block,
            }
            page_blocks.append(item)
            flat_blocks.append(item)
            next_id += 1
        pages.append(page_blocks)

    if not flat_blocks:
        raise RuntimeError("No annotatable text blocks found.")

    work_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        work_dir / "annotation_blocks.json",
        {
            "input_pdf": str(input_pdf),
            "page_count": doc.page_count,
            "block_count": len(flat_blocks),
            "pages": pages,
            "protected_terms": PROTECTED_TERMS,
        },
    )

    chunks_dir = work_dir / "annotation_chunks"
    translations_dir = work_dir / "annotation_translations"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    translations_dir.mkdir(parents=True, exist_ok=True)

    chunk_count = min(chunk_count, len(flat_blocks))
    chunk_size = math.ceil(len(flat_blocks) / chunk_count)
    for chunk_index in range(chunk_count):
        start = chunk_index * chunk_size
        end = min(start + chunk_size, len(flat_blocks))
        chunk_blocks = flat_blocks[start:end]
        output_path = translations_dir / f"annotated_translated_{chunk_index:02d}.json"
        write_json(
            chunks_dir / f"annotation_chunk_{chunk_index:02d}.json",
            {
                "chunk": chunk_index,
                "output_path": str(output_path),
                "instructions": [
                    "Translate each text block into fluent Simplified Chinese for PDF comments.",
                    "Keep the translation concise enough to fit in an annotation popup, but do not omit technical meaning.",
                    "Preserve model names, dataset names, acronyms, formulas, citations, numeric values, section numbering, and URLs.",
                    "Do not translate protected terms unless a conventional Chinese explanation is useful in parentheses.",
                    "Return JSON shaped exactly as {\"translations\":[{\"id\":\"...\",\"zh\":\"...\"}, ...]}.",
                    "Include every block exactly once, in order.",
                ],
                "protected_terms": PROTECTED_TERMS,
                "blocks": [
                    {
                        "id": block["id"],
                        "page": block["page"],
                        "kind": block["kind"],
                        "text": block["text"],
                    }
                    for block in chunk_blocks
                ],
            },
        )

    print(f"Prepared {len(flat_blocks)} annotation blocks across {chunk_count} chunks in {work_dir}")


def collect_translations(work_dir: Path) -> dict[str, str]:
    translations: dict[str, str] = {}
    for path in sorted((work_dir / "annotation_translations").glob("annotated_translated_*.json")):
        payload = load_json(path)
        for item in payload.get("translations", []):
            block_id = item.get("id")
            zh = item.get("zh")
            if isinstance(block_id, str) and isinstance(zh, str):
                translations[block_id] = zh.strip()
    return translations


def status(work_dir: Path) -> None:
    source = load_json(work_dir / "annotation_blocks.json")
    translations = collect_translations(work_dir)
    expected_ids = [block["id"] for page in source["pages"] for block in page]
    missing = [block_id for block_id in expected_ids if block_id not in translations]
    empty = [block_id for block_id in expected_ids if block_id in translations and not translations[block_id]]
    print(f"translated_blocks {len(translations)}")
    print(f"source_blocks {len(expected_ids)}")
    print(f"missing_blocks {len(missing)}")
    print(f"empty_blocks {len(empty)}")
    if missing:
        print("first_missing", " ".join(missing[:20]))
    if empty:
        print("first_empty", " ".join(empty[:20]))


def comment_text(block: dict[str, Any], zh: str) -> str:
    return zh


def build(work_dir: Path, output_pdf: Path, highlight: bool, opacity: float, comment_mode: str) -> None:
    source = load_json(work_dir / "annotation_blocks.json")
    translations = collect_translations(work_dir)
    expected_ids = [block["id"] for page in source["pages"] for block in page]
    missing = [block_id for block_id in expected_ids if block_id not in translations or not translations[block_id]]
    if missing:
        raise RuntimeError(f"Missing or empty translations: {len(missing)}; first: {' '.join(missing[:10])}")

    doc = fitz.open(source["input_pdf"])
    for page_index, page_blocks in enumerate(source["pages"]):
        page = doc[page_index]
        page_rect = page.rect
        for block in page_blocks:
            rect = fitz.Rect(block["bbox"])
            rect &= page_rect
            if rect.is_empty:
                continue
            content = comment_text(block, translations[block["id"]])
            if highlight or comment_mode == "highlight":
                try:
                    hi = page.add_highlight_annot(rect)
                    hi.set_colors(stroke=(1, 0.92, 0.20))
                    hi.set_opacity(max(0.0, min(1.0, opacity)))
                    if comment_mode in ("highlight", "both"):
                        hi.set_info(title="Codex 中文翻译", subject=f"Translation for {block['id']}", content=content)
                    hi.update()
                except Exception:
                    pass
            if comment_mode == "highlight":
                continue
            icon_x = min(page_rect.x1 - 18, rect.x1 + 4)
            icon_y = max(page_rect.y0 + 4, rect.y0)
            if icon_x < rect.x1:
                icon_x = max(page_rect.x0 + 4, rect.x0 - 18)
            annot = page.add_text_annot(
                fitz.Point(icon_x, icon_y),
                content,
                icon="Comment",
            )
            annot.set_info(title="Codex 中文翻译", subject=f"Translation for {block['id']}")
            annot.update()

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    print(f"Wrote {output_pdf}")


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        prepare(args.input_pdf, args.work_dir, args.chunks, args.min_chars)
    elif args.command == "status":
        status(args.work_dir)
    elif args.command == "build":
        build(args.work_dir, args.output_pdf, args.highlight, args.opacity, args.comment_mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
