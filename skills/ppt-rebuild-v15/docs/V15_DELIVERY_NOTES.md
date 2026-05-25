# v15 Delivery Notes

## What Changed

v15 is a conservative upgrade over v14. It does not attempt a full OCR-only or
pixel-perfect inpaint route. It improves the route that worked best in testing:
native PPT reconstruction for structured objects, plus source-image crops for
detailed illustrations and icons.

## New Gate

JSON QA is necessary but not sufficient. A deck is not ready until a rendered
preview is inspected for:

- CJK text wrapping inside labels and cards;
- text-to-text collisions after PowerPoint font substitution;
- cropped image assets covering rebuilt text;
- obvious layout drift from the source screenshot.

## New Reference Page

`examples/paradigm_shift_1_vs_2.scene.json` captures the "1.0 vs 2.0 paradigm
shift" pattern:

- two-column comparison;
- repeated row grammar;
- cropped illustration assets;
- editable badges and descriptions;
- native arrows and dividers.

## Remaining Boundary

v15 still requires a scene graph. It is not a fully automatic image-to-PPT
system. For pages with dense text on complex backgrounds, use cropped/backdrop
fidelity first and rebuild only the important text as editable objects.
