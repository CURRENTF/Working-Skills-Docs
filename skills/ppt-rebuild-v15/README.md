# PPT Rebuild Skill v15

Rebuild image-only PPT slides into editable `.pptx`.

v15 keeps the v14 placement-plan renderer and tightens the delivery gate:
generated PPTX must pass JSON QA and a rendered preview check before handoff.

## Main Modes

```bash
python scripts/run_pipeline.py \
  --scene examples/china_factor_vs_ipcc.scene.json \
  --mode scene \
  --out test/v15_user_image/china_factor_vs_ipcc_rebuilt.pptx
```

With a source slide image:

```bash
python scripts/run_pipeline.py \
  --image input.png \
  --scene scene_graph.json \
  --mode auto \
  --out output/rebuilt_editable.pptx
```

## v15 Policies

- Photos/icons/images are cropped from the source image by bbox when `--image` is supplied.
- Text remains editable as PPT text.
- Native shapes are used for structured tables, cards, arrows, and callouts.
- JSON QA is not enough: always inspect a rendered preview because PPT can wrap text differently after export.
- macOS default PPT font is `PingFang SC`; text bboxes should be adjusted from rendered preview, not only from source-image coordinates.
- `examples/paradigm_shift_1_vs_2.scene.json` is a reference case for two-column 1.0/2.0 comparison pages with cropped illustration assets.

## Test Case

`examples/china_factor_vs_ipcc.scene.json` reconstructs the user-provided comparison slide. The generated PPTX should contain editable title, subtitle, table text, insight text, and KPI cards.

`examples/green_factory_functions_10_12.scene.json` reconstructs the three-card function slide and validates generated SVG+PNG visual assets for green building, employee awareness training, and carbon dashboard illustrations.
