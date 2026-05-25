# Badcase Fix Plan

## Problems observed
1. Text measurement failure caused line wrapping and collisions.
2. Infographic arrows were reconstructed as loose shapes instead of a grammar.
3. Cards did not preserve internal constraints.
4. Output was released without region-level render QA.

## Fixes
1. Use page classifier and template router.
2. Use browser measurement or fallback estimator before PPT generation.
3. Apply constraints per template.
4. Render preview and block bad output.
5. Add dedicated templates for the three observed badcase pages.
