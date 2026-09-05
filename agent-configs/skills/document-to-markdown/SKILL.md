---
name: document-to-markdown
description: >-
  Use only when the user explicitly asks to convert a PDF, Word, PowerPoint,
  Excel, image, HTML document, or document URL into Markdown. Preserve layout,
  tables, formulas, OCR text, and assets when needed. The current MinerU
  backend uploads documents to an external service; obtain explicit approval
  before submitting a document unless the request already authorizes MinerU
  conversion.
---

# Document to Markdown

Convert a user-selected document into Markdown with traceable artifacts for
later reading, research, or ingestion.

## Scope

Own document conversion and its output artifacts; do not summarize, analyze,
or ingest the result unless the user separately asks.

## Trigger

Use this skill only for an explicit request to convert a document or URL to
Markdown.

- Before a MinerU submission, confirm that the user authorizes external upload
  when that authorization is not already clear from the request.
- Do not use it for plain-text files that can be read directly.

## Inputs and outcome

Use the source, fidelity needs, and permitted backend to produce clean Markdown
and enough artifacts to trace conversion errors.

- Input: a local document path or HTTP(S) URL, requested page range, language,
  and whether table, formula, or OCR fidelity matters.
- Input: `MINERU_TOKEN` for standard MinerU mode. Do not store tokens in this
  repository.
- Outcome: `full.md`, a manifest, and extracted assets under
  `.tmp/agent/document-markdown/` unless the user requests a durable location.

## Procedure

Select a backend and conversion options, run the bundled helper, then inspect
the extracted result before handing it to later work.

### Select conversion mode

- Use standard MinerU mode for user-approved, layout-sensitive documents. Use
  `vlm` for complex layouts, tables, or formulas; prefer `pipeline` only when
  speed matters more than fidelity.
- Use `MinerU-HTML` for HTML input. Enable `--ocr` for scans or image-heavy
  documents, and use `--page-ranges` for focused PDF extraction.
- Use lightweight `--mode agent` only for small, low-risk documents or when no
  standard token is available. It is still a backend request, not local parsing.

### Convert and inspect

Run `scripts/document_to_markdown.py` with the selected source and output root.

```bash
python scripts/document_to_markdown.py <source> \
  --out-dir .tmp/agent/document-markdown
```

- Preserve `result.zip`, `manifest.json`, and `extracted/` when output assets,
  tables, formulas, or image links need later inspection.
- Inspect `full.md` for missing text, malformed tables, formulas, and asset
  links before using it downstream.
- Keep the original source path with `full.md` in any handoff.

### Resolve failures

Read [MinerU API notes](references/mineru-api.md) for endpoint, parameter, or
error-code facts. Read [MinerU troubleshooting](references/mineru-troubleshooting.md)
for upload, polling, result-download, proxy, TUN, or fake-IP failures.

## Completion

Report the original source, selected mode, output directory, `full.md` path,
and any known fidelity limitation.

Do not delete conversion artifacts or start downstream analysis without user
direction.

## References

- [MinerU API notes](references/mineru-api.md) — current backend details.
- [MinerU troubleshooting](references/mineru-troubleshooting.md) — conversion
  and network failure diagnosis.
