#!/usr/bin/env python3
"""Convert documents to Markdown with the configured document parsing backend."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shutil
import socket
import ssl
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

# MinerU serves result ZIPs from this CDN host. Under TUN-mode proxies with
# fake-ip DNS, the local resolver returns a dead-end 198.18.x.x / 240.x.x.x
# range for it while the API host (mineru.net) still tunnels correctly.
# preflight_cdn_check detects that case and fills in real IPs so the download
# can use direct TLS with SNI preservation, with no HTTP proxy port required.
CDN_HOST = "cdn-mineru.openxlab.org.cn"
FALLBACK_CDN_IPS = ["8.222.80.133", "8.222.82.255"]
FAKE_IP_PREFIXES = ("198.18.", "198.19.", "240.")


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
        if connection.sock is None:
            raise MinerUError(f"Upload connection to {parsed.netloc} was not established")
        with path.open("rb") as handle:
            shutil.copyfileobj(handle, connection.sock.makefile("wb", buffering=0))
        response = connection.getresponse()
        status = response.status
        detail = response.read().decode("utf-8", errors="replace")
    except (OSError, AttributeError) as exc:
        raise MinerUError(f"Upload failed: {exc}") from exc
    finally:
        connection.close()
    if not (200 <= status < 300):
        raise MinerUError(f"Upload failed with HTTP {status}: {detail}")


def parse_resolve_entries(entries: list[str] | None) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for entry in entries or []:
        if "=" not in entry:
            raise MinerUError(f"--resolve must use host=ip1,ip2 syntax: {entry}")
        host, values = entry.split("=", 1)
        host = host.strip().lower()
        ips = [value.strip() for value in values.split(",") if value.strip()]
        if not host or not ips:
            raise MinerUError(f"--resolve must use host=ip1,ip2 syntax: {entry}")
        mapping[host] = ips
    return mapping


def is_valid_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if int(part) > 255:
            return False
    return True


def is_fake_ip(ip: str) -> bool:
    """Clash/mihomo fake-ip ranges: 198.18.0.0/15 and 240.0.0.0/4 (class E)."""
    return ip.startswith(FAKE_IP_PREFIXES)


def resolve_via_doh(host: str, timeout: int = 10) -> list[str]:
    """Resolve a host to IPv4 addresses via DNS-over-HTTPS.

    DoH endpoints are public IPs routed through the TUN tunnel even when the
    local resolver returns fake-ip ranges for the CDN host. Tries Cloudflare
    first, then Google. Returns an empty list if both fail.
    """
    endpoints = [
        f"https://1.1.1.1/dns-query?name={urllib.parse.quote(host)}&type=A",
        f"https://dns.google/resolve?name={urllib.parse.quote(host)}&type=A",
    ]
    for endpoint in endpoints:
        try:
            request = urllib.request.Request(endpoint, headers={"Accept": "application/dns-json"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            answers = data.get("Answer") or []
            ips = [
                answer["data"]
                for answer in answers
                if answer.get("type") == 1 and is_valid_ipv4(answer.get("data", ""))
            ]
            if ips:
                return ips
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, ValueError):
            continue
    return []


def preflight_cdn_check(args: argparse.Namespace) -> dict[str, list[str]]:
    """Detect TUN-mode fake-ip routing for the MinerU CDN and auto-fill a
    real-IP override so the result-ZIP download succeeds without an HTTP proxy.

    Silent in the dominant case: when the local resolver returns a real IP for
    the CDN host, this returns an empty map (plus any explicit ``--resolve``
    entries) and the normal urllib download path runs unchanged. Only when
    fake-ip is actually detected does it DoH-fetch real IPs and print a
    one-line diagnostic to stderr.
    """
    resolve = parse_resolve_entries(args.resolve)
    if CDN_HOST in resolve:
        return resolve

    try:
        ips = socket.gethostbyname_ex(CDN_HOST)[2]
    except (socket.gaierror, OSError):
        return resolve

    fake = [ip for ip in ips if is_fake_ip(ip)]
    if not fake:
        return resolve

    real_ips = resolve_via_doh(CDN_HOST)
    source = "DoH"
    if not real_ips:
        real_ips = list(FALLBACK_CDN_IPS)
        source = "fallback (DoH failed; IPs may rotate)"
    print(
        f"preflight: {CDN_HOST} resolves to fake-ip {fake} (TUN mode); "
        f"using real IPs {real_ips} via {source} for direct TLS + SNI",
        file=sys.stderr,
    )
    resolve[CDN_HOST] = real_ips
    return resolve


def proxy_host_port(proxy: str) -> tuple[str, int]:
    parsed = urllib.parse.urlparse(proxy)
    if parsed.scheme not in {"http", "https"}:
        raise MinerUError(f"Only http(s) proxies are supported for resolved downloads: {proxy}")
    if not parsed.hostname or not parsed.port:
        raise MinerUError(f"Proxy must include host and port: {proxy}")
    return parsed.hostname, parsed.port


def effective_proxy(explicit: str | None) -> str | None:
    if explicit is not None:
        return explicit or None
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        value = os.environ.get(key)
        if value:
            return value
    return None


def _https_get_to_file(tls: ssl.SSLSocket, host: str, target: str, tmp_path: Path) -> None:
    """Send an HTTP/1.1 GET over an established TLS socket and stream the
    response body to ``tmp_path``. Validates Content-Length when present.

    Shared by the proxy-CONNECT and direct-resolved download paths.
    """
    request = (
        f"GET {target} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "User-Agent: document-to-markdown/1.0\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n\r\n"
    ).encode("ascii")
    tls.sendall(request)
    raw = b""
    while b"\r\n\r\n" not in raw:
        chunk = tls.recv(4096)
        if not chunk:
            break
        raw += chunk
    header_bytes, _, body = raw.partition(b"\r\n\r\n")
    status = header_bytes.split(b"\r\n", 1)[0]
    if b" 200 " not in status:
        raise MinerUError(f"Download GET failed: {status.decode('ascii', errors='replace')}")
    content_length: int | None = None
    for hdr_line in header_bytes.split(b"\r\n")[1:]:
        if hdr_line.lower().startswith(b"content-length:"):
            content_length = int(hdr_line.split(b":", 1)[1].strip())
            break
    with tmp_path.open("wb") as handle:
        written = 0
        if body:
            handle.write(body)
            written += len(body)
        while True:
            chunk = tls.recv(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
            written += len(chunk)
    if content_length is not None and written != content_length:
        raise MinerUError(f"Truncated download: expected {content_length} bytes, got {written}")


def download_via_resolved_connect(
    url: str,
    path: Path,
    proxy: str,
    ips: list[str],
    timeout: int,
    attempts: int,
) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise MinerUError(f"Resolved CONNECT fallback only supports https URLs: {url}")
    host = parsed.hostname
    port = parsed.port or 443
    target = parsed.path or "/"
    if parsed.query:
        target = f"{target}?{parsed.query}"
    proxy_host, proxy_port = proxy_host_port(proxy)
    tmp_path = path.with_suffix(path.suffix + ".part")
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        ip = ips[(attempt - 1) % len(ips)]
        try:
            sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
            tls_wrapped = False
            try:
                connect = (
                    f"CONNECT {ip}:{port} HTTP/1.1\r\n"
                    f"Host: {ip}:{port}\r\n"
                    "Proxy-Connection: Keep-Alive\r\n\r\n"
                ).encode("ascii")
                sock.sendall(connect)
                response = b""
                while b"\r\n\r\n" not in response:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                status_line = response.split(b"\r\n", 1)[0]
                if b" 200 " not in status_line:
                    raise MinerUError(f"Proxy CONNECT failed: {status_line.decode('ascii', errors='replace')}")

                context = ssl.create_default_context()
                with context.wrap_socket(sock, server_hostname=host) as tls:
                    tls_wrapped = True
                    _https_get_to_file(tls, host, target, tmp_path)
            except Exception:
                if not tls_wrapped:
                    sock.close()
                raise
            tmp_path.replace(path)
            return
        except Exception as exc:
            last_error = exc
            time.sleep(min(2 * attempt, 10))

    raise MinerUError(f"Resolved CONNECT download failed after {attempts} attempts: {last_error}")


def download_via_resolved_direct(
    url: str,
    path: Path,
    ips: list[str],
    timeout: int,
    attempts: int,
) -> None:
    """Download via direct TLS to a resolved IP, preserving the original
    hostname as SNI. No HTTP proxy required — this is the path that works
    under TUN-mode proxies that expose no HTTP listener.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise MinerUError(f"Resolved direct download only supports https URLs: {url}")
    host = parsed.hostname
    port = parsed.port or 443
    target = parsed.path or "/"
    if parsed.query:
        target = f"{target}?{parsed.query}"
    tmp_path = path.with_suffix(path.suffix + ".part")
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        ip = ips[(attempt - 1) % len(ips)]
        sock = None
        tls_wrapped = False
        try:
            sock = socket.create_connection((ip, port), timeout=timeout)
            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname=host) as tls:
                tls_wrapped = True
                _https_get_to_file(tls, host, target, tmp_path)
            tmp_path.replace(path)
            return
        except Exception as exc:
            if not tls_wrapped and sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass
            last_error = exc
            time.sleep(min(2 * attempt, 10))

    raise MinerUError(f"Resolved direct download failed after {attempts} attempts: {last_error}")


def download(
    url: str,
    path: Path,
    timeout: int = 300,
    attempts: int = 5,
    proxy: str | None = None,
    resolve: dict[str, list[str]] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".part")
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    last_error: Exception | None = None

    # When real IPs are known (preflight detected fake-ip, or user --resolve),
    # skip urllib — it would connect to the fake-ip dead-end under TUN mode —
    # and go straight to direct TLS with SNI preservation. Falls back to the
    # proxy-CONNECT path only if a proxy is configured and direct-to-IP fails.
    if resolve and host in resolve:
        ips = resolve[host]
        try:
            download_via_resolved_direct(url, path, ips, timeout, attempts)
            return
        except MinerUError as exc:
            if not proxy:
                raise
            last_error = exc
        download_via_resolved_connect(url, path, proxy, ips, timeout, attempts)
        return

    # Dominant path: plain urllib with optional proxy.
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy}) if proxy else urllib.request.ProxyHandler({})
    )

    for attempt in range(1, attempts + 1):
        resume_from = tmp_path.stat().st_size if tmp_path.exists() else 0
        headers = {}
        if resume_from:
            headers["Range"] = f"bytes={resume_from}-"
        request = urllib.request.Request(url, headers=headers)
        try:
            with opener.open(request, timeout=timeout) as response:
                if resume_from and response.status == 200:
                    resume_from = 0
                mode = "ab" if resume_from and response.status == 206 else "wb"
                with tmp_path.open(mode) as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
            tmp_path.replace(path)
            return
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = MinerUError(f"HTTP {exc.code}: {detail}")
            if exc.code not in {408, 429, 500, 502, 503, 504}:
                tmp_path.unlink(missing_ok=True)
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, ssl.SSLError) as exc:
            last_error = exc
        time.sleep(min(2 * attempt, 10))

    raise MinerUError(f"Download failed after {attempts} attempts: {last_error}")


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
    resolve = preflight_cdn_check(args)
    download(full_zip_url, zip_path, proxy=effective_proxy(args.proxy), resolve=resolve)
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
    resolve = preflight_cdn_check(args)
    download(markdown_url, markdown_path, proxy=effective_proxy(args.proxy), resolve=resolve)

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
    parser.add_argument("--proxy", help="HTTP proxy URL for result downloads. Defaults to HTTPS_PROXY or HTTP_PROXY env var if set. Pass empty string to disable.")
    parser.add_argument(
        "--resolve",
        action="append",
        help="Force result downloads for a host through specific IPs, syntax host=ip1,ip2. Useful with proxy CONNECT and SNI.",
    )
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
