# Document to Markdown TODO

## Fallback Conversion Backends

Do not implement these until the current MinerU workflow has a clear failure mode or the user asks for a fallback. The current priority is to keep the main flow stable and diagnosable.

### Middle Option: Local Model Backend

- Evaluate a local deployment option for layout-aware PDF/image OCR and Markdown generation.
- Candidate categories: local MinerU deployment, local VLM/OCR pipeline, or a self-hosted document parser with GPU support.
- Required behavior before adoption:
  - No external data upload.
  - Stable table and layout extraction for Chinese research reports.
  - Clear install/runtime requirements.
  - Batch conversion support.
  - Comparable output shape: `full.md`, manifest, extracted assets.

### Final Option: Local Library Backend Without Model Dependency

- Evaluate deterministic local libraries for fallback extraction when model/OCR quality is not required.
- Candidate categories: `pymupdf`, `pdfplumber`, `pypdf`, `unstructured`, `marker` without remote services, Office parsers for docx/pptx/xlsx.
- Intended use:
  - Text-native PDFs.
  - Fast partial extraction.
  - Emergency fallback when MinerU/API/network is unavailable.
- Limitations to document:
  - Weaker layout reconstruction.
  - Poor scanned-PDF handling without OCR.
  - Tables may need post-processing.

### Integration Notes

- Preserve the current command-line contract where possible.
- Add an explicit `--backend` argument only when at least one fallback is implemented.
- Never silently switch backend for user documents or private workspace data unless the user has authorized fallback behavior.
