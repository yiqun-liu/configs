# MinerU Troubleshooting

Use this guide when `document_to_markdown.py` fails during MinerU upload, polling, result ZIP download, or Markdown extraction. Keep the diagnosis concrete: identify which stage failed before changing the workflow.

## Preflight auto-bypass

The helper runs a preflight before each conversion that resolves `cdn-mineru.openxlab.org.cn` through the local DNS. Under TUN-mode proxies (Clash Verge, mihomo, sing-box) the local resolver returns a fake-ip in `198.18.0.0/15` or `240.0.0.0/4`, and the preflight auto-fetches real IPs via DoH (`1.1.1.1`, then `dns.google`) and downloads the result ZIP via direct TLS with SNI preservation — no HTTP proxy port required, no user flags required.

A successful preflight activation looks like this on stderr:

```
preflight: cdn-mineru.openxlab.org.cn resolves to fake-ip ['198.18.0.40'] (TUN mode); using real IPs ['8.222.82.255', '8.222.80.133'] via DoH for direct TLS + SNI
```

The dominant no-proxy scenario is untouched: when the local resolver returns a real IP, the preflight returns an empty map and the plain urllib download path runs unchanged with zero overhead.

The rest of this guide covers cases the preflight **can't** handle: DoH unreachable, stale fallback IPs, proxy/CDN combinations where direct-to-IP is itself blocked, or non-TUN failures.

## Fast Triage

1. Confirm the credential exists:

```powershell
echo $env:MINERU_TOKEN
```

2. Confirm the local input is readable and not a zero-byte or partial file:

```powershell
Get-Item ".\input.pdf" | Select-Object FullName,Length
```

3. Run the conversion with explicit timeout and interval:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr --language ch --timeout 1200 --interval 5
```

4. If upload and polling succeed but result ZIP download fails, the script auto-detects proxy from `HTTPS_PROXY` / `HTTP_PROXY` environment variables. If those are not set, pass `--proxy` explicitly:

```powershell
python .\scripts\document_to_markdown.py ".\input.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr --language ch --timeout 1200 --interval 5 --proxy http://127.0.0.1:7899
```

Pass `--proxy ""` to explicitly disable proxy even if the environment variables are set. The helper expects an HTTP proxy URL for result downloads.

## TUN / Fake-IP Pattern

Known symptom:

- MinerU task submission and polling complete (the conversion succeeded on MinerU's side).
- Downloading the result from `cdn-mineru.openxlab.org.cn` fails with SSL EOF, TLS handshake failure, or repeated retry exhaustion.
- Local DNS returns a fake-ip range: `198.18.0.x` (Clash/mihomo default) or `240.x.x.x` (class E).

Root cause: the TUN-mode proxy routes the `.cn` CDN host `DIRECT` (China-domain rule), but `DIRECT` connects to the fake-ip `198.18.0.x`, which is a dead end. The API host `mineru.net` typically still tunnels correctly because its rule sends it through a proxy node, which is why submit/poll succeed while the CDN download fails. This is a proxy routing issue, not an SSH configuration issue; `.ssh/config` is unrelated unless the failing command is genuinely using SSH.

The preflight (see above) auto-detects this case and bypasses it without any user flags. If the symptom persists **after** the preflight line appears on stderr, the preflight's DoH fetch or fallback IPs failed — fall back to the manual `--resolve` and `--proxy` flags documented in SKILL.md's "Commands" section (`--resolve` now works without `--proxy`; combine them only when direct-to-IP is itself blocked).

Do not replace the preflight with a silent fallback unless the user has authorized fallback behavior. Report the exact failed stage and the command attempted.

## Diagnostic Commands

Check local proxy listeners:

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalAddress -in @("127.0.0.1","0.0.0.0") -and $_.LocalPort -in 7897,7898,7899,9090,9097 } | Select-Object LocalAddress,LocalPort,OwningProcess
```

```bash
ss -tln | awk 'NR>1 {split($4,a,":"); print a[length(a)]}' | sort -u
```

Check whether DNS is returning fake-ip:

```powershell
Resolve-DnsName cdn-mineru.openxlab.org.cn
```

```bash
getent ahosts cdn-mineru.openxlab.org.cn   # 198.18.x.x or 240.x.x.x = fake-ip
```

A `198.18.0.x` or `240.x.x.x` result is expected in many TUN/fake-ip setups and explains why direct TLS fails. To fetch the real CDN IP outside fake-ip DNS, query a public DoH resolver (it tunnels correctly because it's a non-`.cn` host):

```bash
curl -s 'https://1.1.1.1/dns-query?name=cdn-mineru.openxlab.org.cn&type=A' -H 'Accept: application/dns-json'
```

Confirm the real IP is directly reachable with SNI preserved (HTTP 403 at the CDN root is fine — it means TLS succeeded, the CDN just rejects a bare request):

```bash
curl -sS -o /dev/null -w "HTTP %{http_code}\n" --resolve cdn-mineru.openxlab.org.cn:443:8.222.80.133 https://cdn-mineru.openxlab.org.cn/ -I
```

Check basic proxy connectivity:

```powershell
curl.exe -x http://127.0.0.1:7899 https://www.baidu.com/ -I
```

```bash
curl -x http://127.0.0.1:7899 https://www.baidu.com/ -I   # fails if TUN is proxy-only with no HTTP listener
```

If this fails, fix Clash/port configuration first before debugging MinerU.

## Error Interpretation

| Symptom | Likely stage | First action |
| --- | --- | --- |
| `A0202` or `A0211` | Authentication | Refresh `MINERU_TOKEN`; keep the `Bearer` format inside the helper |
| `-60005` or `-60006` | MinerU limit | Split the file or use page ranges |
| `-60018` | MinerU quota | Stop retrying; wait for quota reset or ask user for another account/source |
| Upload URL request fails | API or auth | Check token, network, and MinerU API status |
| Polling times out | Backend processing | Increase `--timeout`; preserve task id for retry |
| Result ZIP SSL EOF | CDN download | Preflight should auto-bypass; if it didn't, see SKILL.md "Commands" for `--resolve` (and `--proxy`+`--resolve` as deeper fallback) |
| ZIP downloads but no `full.md` | Extraction/output | Inspect `manifest.json` and extracted files before summarizing |

## Current Known Good Pattern

Under TUN mode, the bare command is enough — the preflight auto-detects fake-ip and bypasses it:

```bash
python scripts/document_to_markdown.py ~/input.pdf --out-dir .tmp/agent/document-markdown --model-version vlm --language en
```

A `preflight: ... using real IPs ... via DoH` line on stderr confirms the bypass is active. If DoH is unreachable or the fallback IPs are stale, override with `--resolve` (no `--proxy` needed):

```bash
python scripts/document_to_markdown.py ~/input.pdf --out-dir .tmp/agent/document-markdown --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

Deepest fallback — direct-to-IP blocked, CDN only reachable through the proxy node — `--proxy` + `--resolve`:

```bash
python scripts/document_to_markdown.py ~/input.pdf --out-dir .tmp/agent/document-markdown --proxy http://127.0.0.1:7899 --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

PowerShell equivalents use `.\scripts\document_to_markdown.py` and `.\.tmp\agent\document-markdown` paths. Prefer HTTP(S) proxy URLs for this helper. Pass `--proxy ""` to disable proxy even when `HTTPS_PROXY` is set.

## Reporting Standard

When conversion still fails, report:

- Input path or URL.
- Whether local validation passed.
- Whether upload, polling, result download, and extraction each succeeded.
- MinerU `task_id`, `trace_id`, `err_code`, and `err_msg` when available.
- Proxy and resolve arguments used.
- Whether a fallback was authorized by the user.
