---
name: document-to-markdown
description: Convert PDF, Word, PowerPoint, Excel, image, and HTML documents into clean, LLM-friendly Markdown. Use when Codex needs to parse a local file or document URL, OCR scanned documents, preserve tables/formulas where possible, extract structured Markdown and assets, or prepare source documents for downstream LLM reading, summarization, knowledge-base ingestion, or research workflows.
---

# Document to Markdown

## Overview

Use this skill when normal text extraction is likely to lose layout, tables, formulas, OCR text, images, or document structure. The current backend is MinerU; treat that as an implementation detail and expose the result as clean Markdown plus traceable conversion artifacts.

Prefer the token-based standard backend for user files. Use the lightweight no-token mode only for small, low-risk documents or when no token is available.

## Quick Start

Run the bundled helper script instead of hand-writing backend API calls:

```powershell
python .\scripts\document_to_markdown.py "D:\path\paper.pdf" --out-dir ".\.tmp\agent\document-markdown"
```

For URL input:

```powershell
python .\scripts\document_to_markdown.py "https://example.com/report.pdf" --out-dir ".\.tmp\agent\document-markdown"
```

The script prints a JSON summary containing the task id, output directory, Markdown path, and downloaded ZIP path when applicable.

## Workflow

1. Confirm the backend credential is available before using standard mode. For the current MinerU backend, this is `MINERU_TOKEN`.
2. Choose input mode:
   - Local file: let the script request a signed upload URL, upload the file, poll the result, download the result ZIP, and extract `full.md`.
   - Remote URL: let the script submit the URL task, poll the task, download the result ZIP, and extract `full.md`.
3. Prefer `--model-version vlm` for complex PDFs with layout, formulas, and tables. Use `pipeline` when speed matters more than deep layout accuracy. Use `MinerU-HTML` only for HTML input.
4. Enable OCR with `--ocr` for scanned PDFs or image-heavy files.
5. Use `--page-ranges` for a focused extraction when the user only needs part of a PDF.
6. Inspect the generated Markdown before summarizing or ingesting it. If the output contains broken image links, preserve the extracted ZIP directory so assets can be traced.

## Commands

Standard backend, local PDF:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr --language ch
```

Standard backend, local PDF when MinerU result downloads fail behind Clash/TUN:

If `HTTPS_PROXY` or `HTTP_PROXY` is set in the environment, the script uses it automatically. Otherwise pass `--proxy` explicitly:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr --language ch --proxy http://127.0.0.1:7899
```

If the failure is specific to `cdn-mineru.openxlab.org.cn`, add a temporary real-IP override gathered from trusted DNS:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr --language ch --proxy http://127.0.0.1:7899 --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

Standard backend, URL with page range:

```powershell
python .\scripts\document_to_markdown.py "https://example.com/input.pdf" --page-ranges "1-20" --out-dir ".\.tmp\agent\document-markdown"
```

Lightweight no-token mode for small documents:

```powershell
python .\scripts\document_to_markdown.py ".\small.pdf" --mode agent --out-dir ".\.tmp\agent\document-markdown"
```

Request extra exported formats from the standard backend:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --extra-format html --extra-format docx
```

## Output Conventions

Use a stable output directory for converted documents. Prefer `.tmp/agent/document-markdown/` for agent-run conversions unless the user asks to preserve the conversion artifacts somewhere durable. The helper creates one subdirectory per input and writes:

- `full.md`: extracted Markdown for LLM use.
- `result.zip`: standard backend output ZIP, unless `--no-keep-zip` is set.
- `manifest.json`: task metadata, source path/URL, and result URLs.
- `extracted/`: unpacked ZIP contents for assets and JSON outputs.

Prefer handing downstream agents the `full.md` path plus the original file path. If table/formula fidelity matters, keep `manifest.json` and `extracted/` available for follow-up inspection.

## References

Read `references/mineru-api.md` only when you need current MinerU backend endpoint details, limits, parameter names, or error-code guidance.

Read `references/mineru-troubleshooting.md` when MinerU upload, polling, or result download fails, especially on Windows machines using Clash Verge Rev, TUN mode, fake-ip DNS, or local HTTP/SOCKS proxy ports.
