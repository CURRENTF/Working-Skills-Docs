# v14 Architecture

## Badcase Diagnosis
v13 described template routing but did not render from template plans. Templates returned empty `placements`, and the PPTX builder drew raw scene objects only. That made the system look template-aware while behaving like a bbox-to-PPT demo.

v14 fixes the execution path:

1. route page type;
2. materialize source assets by cropping photos/icons/images from the original slide image;
3. if source assets are unavailable, generate SVG source assets plus PNG fallbacks from `asset_kind` / `asset_prompt`;
4. build a real placement plan;
5. render PPTX from placements;
6. audit editable text, overflow, text overlap, and rendered preview.

## Rendering Strategies

- `scene`: native editable reconstruction from scene objects.
- `auto + image`: crop assets, create textless backdrop when needed, and overlay editable text.
- template plans: accepted only when they return non-empty `placements`.

## Asset Strategy
Photos, equipment images, icons, and detailed visual material must be cropped from the original image first. SVG/native redraw is allowed only for simple icons when the visual match is reliable. Regeneration is a fallback requiring explicit user acceptance.

If the source image is not available, v14 can generate local SVG+PNG assets for common slide illustrations. The SVG is retained for editability, and the PNG is inserted into PPTX for compatibility.

## Text Overlap Lesson
JSON bbox QA can pass while exported PPT still overlaps because PowerPoint text layout uses different font metrics. v14 converts source-image pixels to PPT points and requires rendered preview review before delivery.
