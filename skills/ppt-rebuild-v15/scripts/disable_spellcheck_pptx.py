from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
ET.register_namespace("a", A_NS)


def patch_xml(xml_bytes: bytes) -> tuple[bytes, int]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return xml_bytes, 0

    changed = 0
    text_property_tags = {
        f"{{{A_NS}}}rPr",
        f"{{{A_NS}}}defRPr",
        f"{{{A_NS}}}endParaRPr",
    }
    for text_props in root.iter():
        if text_props.tag not in text_property_tags:
            continue
        if text_props.get("noProof") != "1":
            text_props.set("noProof", "1")
            changed += 1
        if text_props.get("lang") != "zh-CN":
            text_props.set("lang", "zh-CN")
            changed += 1
        if text_props.get("dirty") != "0":
            text_props.set("dirty", "0")
            changed += 1
        if text_props.get("smtClean") != "0":
            text_props.set("smtClean", "0")
            changed += 1
        if "err" in text_props.attrib:
            del text_props.attrib["err"]
            changed += 1

    if changed == 0:
        return xml_bytes, 0
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changed


def disable_spellcheck(src: Path, dst: Path) -> dict[str, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    counters = {"xml_parts": 0, "patched_parts": 0, "patched_attrs": 0}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp:
        tmp_path = Path(tmp.name)

    try:
        with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                should_patch = (
                    info.filename.startswith("ppt/slides/")
                    or info.filename.startswith("ppt/slideLayouts/")
                    or info.filename.startswith("ppt/slideMasters/")
                    or info.filename.startswith("ppt/notesSlides/")
                ) and info.filename.endswith(".xml")

                if should_patch:
                    counters["xml_parts"] += 1
                    data, changed = patch_xml(data)
                    if changed:
                        counters["patched_parts"] += 1
                        counters["patched_attrs"] += changed

                zout.writestr(info, data)

        shutil.move(str(tmp_path), dst)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return counters


def main() -> None:
    parser = argparse.ArgumentParser(description="Disable PowerPoint spellcheck red squiggles for generated PPTX text.")
    parser.add_argument("--src", required=True, type=Path)
    parser.add_argument("--dst", required=True, type=Path)
    args = parser.parse_args()

    print(disable_spellcheck(args.src, args.dst))


if __name__ == "__main__":
    main()
