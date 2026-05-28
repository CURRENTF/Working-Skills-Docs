---
name: annotate-pdf-zh
description: Translate text-based PDFs into Simplified Chinese PDF annotations while preserving the original PDF layout, formulas, figures, tables, and page geometry. Use when the user asks to translate an English or mixed-language PDF into Chinese comments, annotated PDF, 批注翻译, PDF 高亮翻译, or wants readable Chinese help without rebuilding/reflowing the PDF.
---

# Annotate PDF With Chinese Comments

Create an annotated copy of a text-based PDF. Keep the original PDF pages unchanged, highlight each extracted paragraph/table-caption/title block, and store the Chinese translation in the PDF annotation content.

Use this skill instead of rebuilding a Chinese PDF when the source document has dense formulas, tables, charts, multi-column layout, or publisher styling.

## Workflow

1. Verify the PDF has an extractable text layer. If extraction is empty, switch to OCR before using this skill.
2. Use the bundled Codex Python runtime from `load_workspace_dependencies` when available.
3. Ensure `PyMuPDF` is installed in that runtime:

```bash
'<bundled-codex-python>' -m pip install pymupdf
```

4. Prepare paragraph-level annotation chunks:

```bash
'<bundled-codex-python>' scripts/annotate_pdf_workflow.py prepare \
  input.pdf \
  /tmp/pdf-annotation-work \
  --chunks 8 \
  --min-chars 18
```

5. Spawn `worker` sub-agents with model `gpt-5.3-codex-spark`. Assign each worker exactly one `annotation_chunks/annotation_chunk_XX.json` and one matching output path under `annotation_translations/annotated_translated_XX.json`.
6. Ask each worker to write valid JSON shaped exactly as:

```json
{"translations":[{"id":"a00000","zh":"中文译文"}]}
```

7. Check completion:

```bash
'<bundled-codex-python>' scripts/annotate_pdf_workflow.py status /tmp/pdf-annotation-work
```

8. Build the clean annotated PDF:

```bash
'<bundled-codex-python>' scripts/annotate_pdf_workflow.py build \
  /tmp/pdf-annotation-work \
  output-annotated-zh.pdf \
  --highlight \
  --opacity 0.10 \
  --comment-mode highlight
```

9. Render representative pages with `pdftoppm` and inspect them. Check at least the first page, a formula-heavy page, a figure/table page, and the last page.

## Worker Prompt Requirements

Give each worker these requirements:

- Translate every block into fluent Simplified Chinese suitable for a technical PDF comment.
- Keep translations concise enough for annotation popups, but do not omit technical meaning.
- Preserve IDs exactly and keep output order identical to the input.
- Preserve model names, dataset names, acronyms, formulas, citations, numeric values, section numbering, and URLs.
- For formula-heavy or table-like blocks, translate surrounding prose and preserve mathematical notation; do not invent missing symbols.
- For references, preserve author names, venues, years, DOI/arXiv/URLs; translate only titles or short explanatory text when useful.
- Do not use Google Translate or external translation APIs.
- Validate with `json.load` and verify output count equals input block count before finishing.

## Output Modes

Prefer the clean mode:

- `--comment-mode highlight`: one highlight annotation per block, with the Chinese translation stored in the highlight content. This avoids sticky-note icons cluttering figures and tables.

Use visible icons only when needed:

- `--comment-mode both`: adds both highlight annotations and sticky-note text annotations. This can help readers whose PDF app does not expose highlight comments reliably, but it clutters the page.

Do not include English source text in comments. The original English is already visible on the PDF page; the annotation content should contain only the Chinese translation.

## Quality Bar

- Keep the original PDF layout intact.
- Confirm every extracted block has exactly one non-empty Chinese translation.
- Confirm there are no duplicate or missing IDs.
- Prefer `--opacity 0.10` for readable but unobtrusive highlighting.
- Tell the user that annotation behavior depends on the PDF reader. Adobe Acrobat usually exposes comments most reliably; browser PDF viewers may be less consistent.
