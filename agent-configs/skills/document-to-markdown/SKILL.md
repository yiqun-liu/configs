---
name: document-to-markdown
description: Convert PDF, Word, PowerPoint, Excel, image, and HTML documents into clean, LLM-friendly Markdown. Use when Codex needs to parse a local file or document URL, OCR scanned documents, preserve tables/formulas where possible, extract structured Markdown and assets, or prepare source documents for downstream LLM reading, summarization, knowledge-base ingestion, or research workflows.
---

# Document to Markdown

## Overview

Use this skill when normal text extraction is likely to lose layout, tables, formulas, OCR text, images, or document structure. The current backend is MinerU; treat that as an implementation detail and expose the result as clean Markdown plus traceable conversion artifacts. A built-in preflight auto-bypasses fake-ip DNS under TUN-mode proxies so the result-ZIP download works without any proxy flags.

Prefer the token-based standard backend for user files. Use the lightweight no-token mode only for small, low-risk documents or when no token is available.

## Quick Start

Run the bundled helper script instead of hand-writing backend API calls. Arguments are identical across shells; only the path separator differs.

Bash/zsh:

```bash
python scripts/document_to_markdown.py ~/docs/paper.pdf --out-dir .tmp/agent/document-markdown
```

PowerShell:

```powershell
python .\scripts\document_to_markdown.py "D:\path\paper.pdf" --out-dir ".\.tmp\agent\document-markdown"
```

For URL input:

```bash
python scripts/document_to_markdown.py "https://example.com/report.pdf" --out-dir .tmp/agent/document-markdown
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

## TUN-mode preflight

Before submitting a task, the helper resolves `cdn-mineru.openxlab.org.cn` through the local DNS. If the result is in the Clash/mihomo fake-ip range (`198.18.0.0/15`, `240.0.0.0/4`), it fetches the CDN's real IPs via DNS-over-HTTPS (`1.1.1.1`, then `dns.google`) and downloads the result ZIP via direct TLS with SNI preservation — no HTTP proxy port required.

This makes the helper work out of the box behind TUN-mode proxies (Clash Verge, mihomo, sing-box) that route the `.cn` CDN host `DIRECT` into the fake-ip dead-end while still tunneling the API host `mineru.net`. The dominant no-proxy scenario is untouched: when the local resolver returns a real IP, the preflight returns immediately and the plain urllib download path runs unchanged.

The preflight prints one diagnostic line to stderr when it activates, e.g.:

```
preflight: cdn-mineru.openxlab.org.cn resolves to fake-ip ['198.18.0.40'] (TUN mode); using real IPs ['8.222.82.255', '8.222.80.133'] via DoH for direct TLS + SNI
```

To override the auto-detected IPs, pass `--resolve cdn-mineru.openxlab.org.cn=<ip1>,<ip2>`; the preflight respects an explicit `--resolve` and skips its own detection for that host.

## Commands

Standard backend, local PDF:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr --language ch
```

Standard backend, local PDF behind a TUN-mode proxy:

The preflight auto-detects fake-ip DNS and bypasses it (see "TUN-mode preflight" above). The manual flags below are only needed when the auto-detection fails — e.g., DoH is unreachable, or the CDN IP has rotated and the fallback list is stale.

`--resolve` now works without `--proxy`: it forces direct TLS to the listed IPs with SNI preserved. Use it to override stale auto-detected IPs:

```bash
python scripts/document_to_markdown.py ~/input.pdf --out-dir .tmp/agent/document-markdown --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

If direct-to-IP is itself blocked (the CDN is only reachable through the proxy node), combine `--proxy` with `--resolve` to CONNECT through the proxy to the real IP:

```bash
python scripts/document_to_markdown.py ~/input.pdf --out-dir .tmp/agent/document-markdown --proxy http://127.0.0.1:7899 --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

If `HTTPS_PROXY` or `HTTP_PROXY` is set in the environment, the script uses it automatically for the plain urllib path; pass `--proxy ""` to disable it.

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

Read `references/mineru-troubleshooting.md` when MinerU upload, polling, or result download fails, or when the TUN-mode preflight can't auto-resolve the CDN (DoH unreachable, stale fallback IPs). Covers Clash Verge Rev / mihomo / sing-box on both Windows and Linux, fake-ip DNS, and local HTTP/SOCKS proxy ports.
