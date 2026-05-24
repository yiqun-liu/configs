# MinerU API Reference Notes

Source: https://mineru.net/apiManage/docs

## Standard API

Use the standard API when the user has a token, wants higher quality, needs larger files, or wants the full ZIP output.

- Base URL: `https://mineru.net`
- Auth header: `Authorization: Bearer <MINERU_TOKEN>`
- Limits documented by MinerU: 200 MB per file, 200 pages per file, batch support.
- Supported types include PDF, images, Word, PowerPoint, Excel, and HTML.
- Models: `pipeline`, `vlm`, `MinerU-HTML`.
- Default Markdown result is in the downloaded ZIP as `full.md`.

Important endpoints:

- URL task: `POST /api/v4/extract/task`
- Local upload/batch: `POST /api/v4/file-urls/batch`
- Single task polling: `GET /api/v4/extract/task/{task_id}`
- Batch polling: `GET /api/v4/extract-results/batch/{batch_id}`

Common parameters:

- `model_version`: `vlm` for high quality, `pipeline` for default/speed, `MinerU-HTML` for HTML.
- `is_ocr`: enable OCR for scanned PDFs.
- `enable_formula`: formula recognition, default true.
- `enable_table`: table recognition, default true.
- `language`: OCR language, default `ch`.
- `page_ranges`: standard API page range syntax, for example `2,4-6`.
- `extra_formats`: optional `docx`, `html`, or `latex`.
- `no_cache` and `cache_tolerance`: control MinerU URL cache behavior.

For local standard uploads through `/api/v4/file-urls/batch`, put `name`, `data_id`, `is_ocr`, and `page_ranges` inside each object in `files`; keep `model_version`, `enable_formula`, `enable_table`, `language`, and `extra_formats` at the top level.

## Lightweight Agent API

Use the Agent API only for small documents, demos, or cases where no token is available.

- No Authorization header.
- Lower limits documented by MinerU: 10 MB and 20 pages.
- Output is only Markdown via `markdown_url`.
- Endpoints:
  - URL task: `POST /api/v1/agent/parse/url`
  - Local upload: `POST /api/v1/agent/parse/file`
  - Polling: `GET /api/v1/agent/parse/{task_id}`
- Page parameter is `page_range`, not `page_ranges`, and supports simpler ranges such as `1-10` or `5`.

## Error Handling

Treat API `code != 0` as failure even when the HTTP status is 200. Include `trace_id`, `msg`, and task state in diagnostics.

Useful documented codes:

- `A0202`: token error, check `Bearer` prefix and token value.
- `A0211`: token expired.
- `-60005`: file size exceeds standard API limit.
- `-60006`: page count exceeds standard API limit.
- `-60008`: URL read timeout or inaccessible URL.
- `-60012`: task not found.
- `-60018`: daily task limit reached.

When a task state is `failed`, report `err_msg` and `err_code` if present.
