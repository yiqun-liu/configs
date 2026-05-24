#!/usr/bin/env python3
"""Convert documents to Markdown with the configured document parsing backend."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


BASE_URL = "https://mineru.net"
DONE_STATES = {"done"}
FAILED_STATES = {"failed"}
WAIT_STATES = {"waiting-file", "uploading", "pending", "running", "converting"}


class MinerUError(RuntimeError):
    pass


def is_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def slugify(value: str) -> str:
    value = urllib.parse.unquote(value)
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", value).strip("-._ ")
    return value[:80] or "mineru-document"


def source_name(source: str, file_name: str | None = None) -> str:
    if file_name:
        return file_name
    if is_url(source):
        path = urllib.parse.urlparse(source).path
        name = Path(path).name
        return name or "url-document.pdf"
    return Path(source).name


def output_dir_for(source: str, out_root: Path, file_name: str | None = None) -> Path:
    name = source_name(source, file_name)
    stem = Path(name).stem or slugify(name)
    return out_root / slugify(stem)


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    body = None
    headers = {"Accept": "*/*"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise MinerUError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MinerUError(f"Request failed for {url}: {exc.reason}") from exc

    try:
        result = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise MinerUError(f"Non-JSON response from {url}: {raw[:500]!r}") from exc

    if result.get("code") != 0:
        trace = result.get("trace_id", "")
        msg = result.get("msg", "unknown error")
        raise MinerUError(f"MinerU API error code={result.get('code')} msg={msg} trace_id={trace}")
    return result


def upload_file(upload_url: str, path: Path, timeout: int = 300) -> None:
    parsed = urllib.parse.urlparse(upload_url)
    if parsed.scheme != "https":
        raise MinerUError(f"Upload URL must use https: {upload_url}")
    target = parsed.path
    if parsed.query:
        target = f"{target}?{parsed.query}"
    connection = http.client.HTTPSConnection(parsed.netloc, timeout=timeout)
    try:
        connection.putrequest("PUT", target)
        connection.putheader("Host", parsed.netloc)
        connection.putheader("Content-Length", str(path.stat().st_size))
        connection.endheaders()
        with path.open("rb") as handle:
            shutil.copyfileobj(handle, connection.sock.makefile("wb", buffering=0))
        response = connection.getresponse()
        status = response.status
        detail = response.read().decode("utf-8", errors="replace")
    except OSError as exc:
        raise MinerUError(f"Upload failed: {exc}") from exc
    finally:
        connection.close()
    if not (200 <= status < 300):
        raise MinerUError(f"Upload failed with HTTP {status}: {detail}")


def download(url: str, path: Path, timeout: int = 300) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            with path.open("wb") as handle:
                shutil.copyfileobj(response, handle)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise MinerUError(f"Download failed with HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MinerUError(f"Download failed: {exc.reason}") from exc


def standard_payload(args: argparse.Namespace, source_url: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model_version": args.model_version,
        "is_ocr": args.ocr,
        "enable_formula": not args.disable_formula,
        "enable_table": not args.disable_table,
        "language": args.language,
    }
    if source_url:
        payload["url"] = source_url
    if args.data_id:
        payload["data_id"] = args.data_id
    if args.page_ranges:
        payload["page_ranges"] = args.page_ranges
    if args.extra_format:
        payload["extra_formats"] = args.extra_format
    if args.no_cache:
        payload["no_cache"] = True
    if args.cache_tolerance is not None:
        payload["cache_tolerance"] = args.cache_tolerance
    return payload


def batch_payload(args: argparse.Namespace, file_path: Path) -> dict[str, Any]:
    file_entry: dict[str, Any] = {"name": file_path.name}
    if args.data_id:
        file_entry["data_id"] = args.data_id
    if args.page_ranges:
        file_entry["page_ranges"] = args.page_ranges
    if args.ocr:
        file_entry["is_ocr"] = True
    payload: dict[str, Any] = {
        "files": [file_entry],
        "model_version": args.model_version,
        "enable_formula": not args.disable_formula,
        "enable_table": not args.disable_table,
        "language": args.language,
    }
    if args.extra_format:
        payload["extra_formats"] = args.extra_format
    return payload


def agent_payload(args: argparse.Namespace, source: str | None = None, file_name: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "language": args.language,
        "enable_table": not args.disable_table,
        "is_ocr": args.ocr,
        "enable_formula": not args.disable_formula,
    }
    if source:
        payload["url"] = source
    if file_name:
        payload["file_name"] = file_name
    if args.page_ranges:
        payload["page_range"] = args.page_ranges
    return payload


def wait_for_task(
    poll_url: str,
    token: str | None,
    timeout_seconds: int,
    interval_seconds: int,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_state = "unknown"
    while time.time() < deadline:
        result = request_json("GET", poll_url, token=token)
        data = result.get("data") or {}
        state = data.get("state")
        if state in DONE_STATES:
            return result
        if state in FAILED_STATES:
            raise MinerUError(f"MinerU task failed: {json.dumps(data, ensure_ascii=False)}")
        last_state = state or last_state
        if state not in WAIT_STATES:
            raise MinerUError(f"Unexpected MinerU task state: {json.dumps(data, ensure_ascii=False)}")
        time.sleep(interval_seconds)
    raise MinerUError(f"Timed out waiting for MinerU task; last state={last_state}")


def batch_result_item(result: dict[str, Any]) -> dict[str, Any]:
    data = result.get("data") or {}
    item = data.get("extract_result") or data.get("extract_results")
    if isinstance(item, list):
        if not item:
            raise MinerUError("Batch result is empty")
        item = item[0]
    if not isinstance(item, dict):
        raise MinerUError(f"Unexpected batch result shape: {json.dumps(data, ensure_ascii=False)}")
    return item


def wait_for_batch(batch_id: str, token: str, args: argparse.Namespace) -> dict[str, Any]:
    poll_url = f"{BASE_URL}/api/v4/extract-results/batch/{batch_id}"
    deadline = time.time() + args.timeout
    last_state = "unknown"
    while time.time() < deadline:
        result = request_json("GET", poll_url, token=token)
        item = batch_result_item(result)
        state = item.get("state")
        if state in DONE_STATES:
            return result
        if state in FAILED_STATES:
            raise MinerUError(f"MinerU batch item failed: {json.dumps(item, ensure_ascii=False)}")
        last_state = state or last_state
        if state not in WAIT_STATES:
            raise MinerUError(f"Unexpected MinerU batch state: {json.dumps(item, ensure_ascii=False)}")
        time.sleep(args.interval)
    raise MinerUError(f"Timed out waiting for MinerU batch; last state={last_state}")


def extract_full_markdown(zip_path: Path, extract_dir: Path, markdown_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)
        candidates = [name for name in archive.namelist() if Path(name).name == "full.md"]
        if not candidates:
            raise MinerUError("MinerU ZIP did not contain full.md")
        candidate = candidates[0]
        content = archive.read(candidate).decode("utf-8", errors="replace")
    markdown_path.write_text(content, encoding="utf-8")
    return candidate


def save_manifest(out_dir: Path, manifest: dict[str, Any]) -> Path:
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def parse_standard(args: argparse.Namespace, token: str) -> dict[str, Any]:
    source = args.source
    out_dir = output_dir_for(source, args.out_dir, args.file_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "full.md"
    zip_path = out_dir / "result.zip"
    extract_dir = out_dir / "extracted"

    if is_url(source):
        submit = request_json(
            "POST",
            f"{BASE_URL}/api/v4/extract/task",
            payload=standard_payload(args, source),
            token=token,
        )
        task_id = submit["data"]["task_id"]
        result = wait_for_task(f"{BASE_URL}/api/v4/extract/task/{task_id}", token, args.timeout, args.interval)
        result_data = result["data"]
    else:
        file_path = Path(source).expanduser().resolve()
        if not file_path.is_file():
            raise MinerUError(f"Input file not found: {file_path}")
        submit = request_json(
            "POST",
            f"{BASE_URL}/api/v4/file-urls/batch",
            payload=batch_payload(args, file_path),
            token=token,
        )
        batch_id = submit["data"]["batch_id"]
        file_urls = submit["data"]["file_urls"]
        if not file_urls:
            raise MinerUError("MinerU did not return an upload URL")
        upload_file(file_urls[0], file_path)
        result = wait_for_batch(batch_id, token, args)
        result_data = batch_result_item(result)
        task_id = result_data.get("task_id") or batch_id

    full_zip_url = result_data.get("full_zip_url")
    if not full_zip_url:
        raise MinerUError(f"Done result did not include full_zip_url: {json.dumps(result_data, ensure_ascii=False)}")
    download(full_zip_url, zip_path)
    zip_full_md = extract_full_markdown(zip_path, extract_dir, markdown_path)
    if args.no_keep_zip:
        zip_path.unlink(missing_ok=True)

    manifest = {
        "mode": "standard",
        "source": source,
        "task_id": task_id,
        "full_zip_url": full_zip_url,
        "markdown_path": str(markdown_path),
        "zip_path": str(zip_path) if zip_path.exists() else None,
        "extracted_dir": str(extract_dir),
        "zip_full_md": zip_full_md,
        "result": result,
    }
    manifest["manifest_path"] = str(save_manifest(out_dir, manifest))
    return manifest


def parse_agent(args: argparse.Namespace) -> dict[str, Any]:
    source = args.source
    out_dir = output_dir_for(source, args.out_dir, args.file_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "full.md"

    if is_url(source):
        submit = request_json(
            "POST",
            f"{BASE_URL}/api/v1/agent/parse/url",
            payload=agent_payload(args, source=source, file_name=args.file_name),
        )
    else:
        file_path = Path(source).expanduser().resolve()
        if not file_path.is_file():
            raise MinerUError(f"Input file not found: {file_path}")
        submit = request_json(
            "POST",
            f"{BASE_URL}/api/v1/agent/parse/file",
            payload=agent_payload(args, file_name=args.file_name or file_path.name),
        )
        upload_url = submit["data"]["file_url"]
        upload_file(upload_url, file_path)

    task_id = submit["data"]["task_id"]
    result = wait_for_task(f"{BASE_URL}/api/v1/agent/parse/{task_id}", None, args.timeout, args.interval)
    markdown_url = result["data"].get("markdown_url")
    if not markdown_url:
        raise MinerUError(f"Done result did not include markdown_url: {json.dumps(result['data'], ensure_ascii=False)}")
    download(markdown_url, markdown_path)

    manifest = {
        "mode": "agent",
        "source": source,
        "task_id": task_id,
        "markdown_url": markdown_url,
        "markdown_path": str(markdown_path),
        "result": result,
    }
    manifest["manifest_path"] = str(save_manifest(out_dir, manifest))
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a document to LLM-friendly Markdown.")
    parser.add_argument("source", help="Local file path or http(s) URL.")
    parser.add_argument("--out-dir", type=Path, default=Path(".tmp/agent/document-markdown"), help="Output root directory.")
    parser.add_argument("--mode", choices=["standard", "agent"], default="standard", help="Backend API mode.")
    parser.add_argument("--token-env", default="MINERU_TOKEN", help="Environment variable containing the backend token.")
    parser.add_argument("--model-version", default="vlm", choices=["pipeline", "vlm", "MinerU-HTML"], help="Standard API model.")
    parser.add_argument("--language", default="ch", help="Document OCR language, default ch.")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR.")
    parser.add_argument("--disable-formula", action="store_true", help="Disable formula recognition.")
    parser.add_argument("--disable-table", action="store_true", help="Disable table recognition.")
    parser.add_argument("--page-ranges", help="Page range. Standard supports values like 2,4-6; agent supports simple 1-10 or 5.")
    parser.add_argument("--data-id", help="Optional MinerU data_id for standard API tasks.")
    parser.add_argument("--file-name", help="Optional file name for URL type detection or output naming.")
    parser.add_argument("--extra-format", action="append", choices=["docx", "html", "latex"], help="Standard API extra format.")
    parser.add_argument("--no-cache", action="store_true", help="Bypass MinerU URL cache for standard API URL input.")
    parser.add_argument("--cache-tolerance", type=int, help="Cache tolerance in seconds for standard API URL input.")
    parser.add_argument("--timeout", type=int, default=1800, help="Polling timeout in seconds.")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds.")
    parser.add_argument("--no-keep-zip", action="store_true", help="Delete result.zip after extracting full.md.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    try:
        if args.mode == "standard":
            token = os.environ.get(args.token_env)
            if not token:
                raise MinerUError(f"Set {args.token_env} before using --mode standard.")
            manifest = parse_standard(args, token)
        else:
            manifest = parse_agent(args)
    except MinerUError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({k: v for k, v in manifest.items() if k != "result"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
