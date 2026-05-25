from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from PIL import Image, ImageDraw


GENERATABLE_TYPES = {"image", "photo", "icon"}


def _svg(kind: str, width: int, height: int) -> str:
    if kind == "green_building":
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 420 220">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#d9fbf0"/><stop offset="1" stop-color="#b9ecff"/></linearGradient></defs>
<rect width="420" height="220" fill="url(#g)"/>
<rect x="118" y="55" width="190" height="125" rx="6" fill="#68d8d0" stroke="#00385c" stroke-width="4"/>
<path d="M118 55 L215 25 L308 55 Z" fill="#cceef1" stroke="#00385c" stroke-width="4"/>
<g fill="#aef0ff" stroke="#00385c" stroke-width="2">
<rect x="142" y="80" width="38" height="38"/><rect x="186" y="80" width="38" height="38"/><rect x="230" y="80" width="38" height="38"/>
<rect x="142" y="125" width="38" height="38"/><rect x="186" y="125" width="38" height="38"/><rect x="230" y="125" width="38" height="38"/>
</g>
<path d="M92 62 C110 34 139 29 159 53 L159 177 L92 177 Z" fill="#51c958" stroke="#078f60" stroke-width="3"/>
<path d="M102 74 C119 54 135 52 149 70 M101 102 C119 83 137 83 151 99 M101 131 C119 111 137 111 151 128" stroke="#eaffb8" stroke-width="7" fill="none"/>
<g fill="#2675a6" stroke="#00385c" stroke-width="2"><path d="M262 33 L350 17 L378 55 L288 70 Z"/><path d="M282 31 L309 65 M309 24 L337 60 M337 20 L365 55 M276 49 L366 34"/></g>
<g fill="#25b764" stroke="#006c55" stroke-width="3"><circle cx="62" cy="166" r="16"/><rect x="59" y="178" width="6" height="24"/><circle cx="362" cy="158" r="22"/><rect x="358" y="180" width="8" height="25"/></g>
<path d="M35 200 H390" stroke="#0aa588" stroke-width="5" stroke-linecap="round"/>
</svg>'''
    if kind == "awareness_training":
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 420 220">
<rect width="420" height="220" fill="#f8fafb"/>
<rect x="190" y="30" width="110" height="125" rx="3" fill="#eef6f4" stroke="#4e5962" stroke-width="3"/>
<path d="M210 58 H282 M210 78 H270 M210 98 H288" stroke="#8aa1a6" stroke-width="5" stroke-linecap="round"/>
<circle cx="250" cy="120" r="28" fill="#54c990" opacity=".75"/>
<path d="M231 122 L244 135 L272 100" stroke="#0b6f55" stroke-width="7" fill="none" stroke-linecap="round"/>
<g stroke="#2d3b44" stroke-width="3" stroke-linecap="round">
<circle cx="105" cy="108" r="22" fill="#f2b28b"/><path d="M78 183 C85 142 125 142 137 183" fill="#fff"/><path d="M80 182 H146" />
<circle cx="323" cy="105" r="20" fill="#9a684b"/><path d="M290 183 C301 143 343 143 355 183" fill="#d09a62"/><path d="M287 182 H360"/>
<circle cx="170" cy="78" r="18" fill="#f0b58f"/><path d="M147 160 C151 115 190 115 197 160" fill="#fff"/><path d="M148 160 H198"/>
<circle cx="365" cy="122" r="19" fill="#c98b67"/><path d="M336 190 C344 151 383 151 393 190" fill="#4db08c"/>
</g>
<path d="M122 128 C152 108 171 111 197 128 M292 129 C275 117 270 112 258 119" stroke="#596872" stroke-width="4" fill="none"/>
<rect x="60" y="184" width="305" height="13" rx="6" fill="#cbd8dd"/>
</svg>'''
    if kind == "carbon_dashboard":
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 420 220">
<rect width="420" height="220" fill="#f8fafb"/>
<rect x="45" y="30" width="330" height="155" rx="8" fill="#ffffff" stroke="#244763" stroke-width="5"/>
<rect x="45" y="30" width="75" height="155" rx="8" fill="#17364e"/>
<circle cx="64" cy="48" r="4" fill="#ff6b57"/><circle cx="78" cy="48" r="4" fill="#ffd166"/><circle cx="92" cy="48" r="4" fill="#05c793"/>
<rect x="58" y="72" width="46" height="8" rx="4" fill="#08b890"/><rect x="58" y="94" width="38" height="6" rx="3" fill="#74a2b8"/><rect x="58" y="113" width="44" height="6" rx="3" fill="#74a2b8"/>
<rect x="140" y="55" width="110" height="50" rx="5" fill="#edf8f5"/>
<path d="M150 91 C170 68 185 83 201 73 C218 63 226 74 241 60" stroke="#10b790" stroke-width="6" fill="none"/>
<rect x="268" y="55" width="76" height="74" rx="5" fill="#f7f0df"/>
<circle cx="306" cy="91" r="28" fill="none" stroke="#11b890" stroke-width="12"/><path d="M306 63 A28 28 0 0 1 333 98" fill="none" stroke="#d79624" stroke-width="12"/>
<rect x="140" y="122" width="110" height="47" rx="5" fill="#eef3fa"/>
<path d="M152 154 C170 132 184 145 198 139 C218 129 226 144 243 129" stroke="#7ccab2" stroke-width="5" fill="none"/>
<g fill="#0cb793"><rect x="270" y="150" width="13" height="20"/><rect x="292" y="137" width="13" height="33"/><rect x="314" y="117" width="13" height="53"/><rect x="336" y="130" width="13" height="40"/></g>
</svg>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="{width}" height="{height}" rx="16" fill="#e9f7f4"/>
<circle cx="{width/2}" cy="{height/2}" r="{min(width, height)/4}" fill="#00b79b" opacity=".7"/>
</svg>'''


def _draw_green_building(path: Path, size: tuple[int, int]) -> None:
    img = Image.new("RGBA", size, "#dffbf3")
    d = ImageDraw.Draw(img)
    w, h = size
    sx, sy = w / 420, h / 220
    def xy(box): return [int(box[0]*sx), int(box[1]*sy), int(box[2]*sx), int(box[3]*sy)]
    d.polygon([(int(118*sx),int(55*sy)),(int(215*sx),int(25*sy)),(int(308*sx),int(55*sy))], fill="#cceef1", outline="#00385c")
    d.rounded_rectangle(xy([118,55,308,180]), radius=6, fill="#68d8d0", outline="#00385c", width=max(1,int(4*sx)))
    for x in [142,186,230]:
        for y in [80,125]:
            d.rectangle(xy([x,y,x+38,y+38]), fill="#aef0ff", outline="#00385c", width=2)
    d.polygon([(int(92*sx),int(62*sy)),(int(159*sx),int(53*sy)),(int(159*sx),int(177*sy)),(int(92*sx),int(177*sy))], fill="#51c958", outline="#078f60")
    for off in [0,28,57]:
        d.arc(xy([100,60+off,152,98+off]), 190, 345, fill="#eaffb8", width=max(2,int(7*sx)))
    d.polygon([(int(262*sx),int(33*sy)),(int(350*sx),int(17*sy)),(int(378*sx),int(55*sy)),(int(288*sx),int(70*sy))], fill="#2675a6", outline="#00385c")
    for x,y,r in [(62,166,16),(362,158,22)]:
        d.ellipse(xy([x-r,y-r,x+r,y+r]), fill="#25b764", outline="#006c55", width=2)
        d.rectangle(xy([x-3,y+r,x+3,y+r+25]), fill="#006c55")
    d.line([(int(35*sx),int(200*sy)),(int(390*sx),int(200*sy))], fill="#0aa588", width=max(3,int(5*sx)))
    img.save(path)


def _draw_awareness(path: Path, size: tuple[int, int]) -> None:
    img = Image.new("RGBA", size, "#f8fafb")
    d = ImageDraw.Draw(img)
    w, h = size
    sx, sy = w / 420, h / 220
    def xy(box): return [int(box[0]*sx), int(box[1]*sy), int(box[2]*sx), int(box[3]*sy)]
    d.rounded_rectangle(xy([190,30,300,155]), radius=4, fill="#eef6f4", outline="#4e5962", width=3)
    for y, x2 in [(58,282),(78,270),(98,288)]:
        d.line([(int(210*sx),int(y*sy)),(int(x2*sx),int(y*sy))], fill="#8aa1a6", width=4)
    d.ellipse(xy([222,92,278,148]), fill="#54c990")
    d.line([(int(231*sx),int(122*sy)),(int(244*sx),int(135*sy)),(int(272*sx),int(100*sy))], fill="#0b6f55", width=5)
    people=[(105,108,"#f2b28b","#ffffff"),(323,105,"#9a684b","#d09a62"),(170,78,"#f0b58f","#ffffff"),(365,122,"#c98b67","#4db08c")]
    for x,y,skin,body in people:
        d.ellipse(xy([x-20,y-20,x+20,y+20]), fill=skin, outline="#2d3b44", width=2)
        d.rounded_rectangle(xy([x-30,y+22,x+32,y+78]), radius=16, fill=body, outline="#2d3b44", width=2)
    d.line([(int(60*sx),int(190*sy)),(int(365*sx),int(190*sy))], fill="#cbd8dd", width=12)
    img.save(path)


def _draw_dashboard(path: Path, size: tuple[int, int]) -> None:
    img = Image.new("RGBA", size, "#f8fafb")
    d = ImageDraw.Draw(img)
    w, h = size
    sx, sy = w / 420, h / 220
    def xy(box): return [int(box[0]*sx), int(box[1]*sy), int(box[2]*sx), int(box[3]*sy)]
    d.rounded_rectangle(xy([45,30,375,185]), radius=8, fill="#ffffff", outline="#244763", width=4)
    d.rounded_rectangle(xy([45,30,120,185]), radius=8, fill="#17364e")
    for x,c in [(64,"#ff6b57"),(78,"#ffd166"),(92,"#05c793")]:
        d.ellipse(xy([x-4,44,x+4,52]), fill=c)
    d.rounded_rectangle(xy([58,72,104,80]), radius=4, fill="#08b890")
    for y in [94,113,132]:
        d.rounded_rectangle(xy([58,y,102,y+6]), radius=3, fill="#74a2b8")
    d.rounded_rectangle(xy([140,55,250,105]), radius=5, fill="#edf8f5")
    pts=[(150,91),(170,68),(185,83),(201,73),(218,63),(226,74),(241,60)]
    d.line([(int(x*sx),int(y*sy)) for x,y in pts], fill="#10b790", width=4)
    d.rounded_rectangle(xy([268,55,344,129]), radius=5, fill="#f7f0df")
    d.ellipse(xy([278,63,334,119]), outline="#11b890", width=10)
    d.arc(xy([278,63,334,119]), -90, 20, fill="#d79624", width=10)
    d.rounded_rectangle(xy([140,122,250,169]), radius=5, fill="#eef3fa")
    pts=[(152,154),(170,132),(184,145),(198,139),(218,129),(226,144),(243,129)]
    d.line([(int(x*sx),int(y*sy)) for x,y in pts], fill="#7ccab2", width=3)
    for x,top in [(270,150),(292,137),(314,117),(336,130)]:
        d.rectangle(xy([x,top,x+13,170]), fill="#0cb793")
    img.save(path)


def _draw_asset(kind: str, path: Path, size: tuple[int, int]) -> None:
    if kind == "green_building":
        _draw_green_building(path, size)
    elif kind == "awareness_training":
        _draw_awareness(path, size)
    elif kind == "carbon_dashboard":
        _draw_dashboard(path, size)
    else:
        img = Image.new("RGBA", size, "#e9f7f4")
        d = ImageDraw.Draw(img)
        w, h = size
        d.ellipse([w * 0.35, h * 0.25, w * 0.65, h * 0.75], fill="#00b79b")
        img.save(path)


def generate_missing_visual_assets(scene: Dict[str, Any], out_dir: str) -> Dict[str, Any]:
    asset_dir = Path(out_dir)
    asset_dir.mkdir(parents=True, exist_ok=True)
    updated = {**scene, "objects": []}
    sw, sh = scene.get("slide_size", [1600, 900])

    for obj in scene.get("objects", []):
        item = dict(obj)
        if item.get("type") in GENERATABLE_TYPES and not item.get("path"):
            kind = item.get("asset_kind") or item.get("asset_prompt") or "generic"
            _, _, bw, bh = item.get("bbox", [0, 0, 320, 180])
            width = max(240, int(bw))
            height = max(140, int(bh))
            base = asset_dir / item.get("id", "generated_asset")
            svg_path = base.with_suffix(".svg")
            png_path = base.with_suffix(".png")
            svg_path.write_text(_svg(kind, width, height), encoding="utf-8")
            _draw_asset(kind, png_path, (width, height))
            item["type"] = "image"
            item["path"] = str(png_path)
            item["svg_path"] = str(svg_path)
            item["asset_strategy"] = "generated_svg_with_png_fallback"
        updated["objects"].append(item)
    return updated
