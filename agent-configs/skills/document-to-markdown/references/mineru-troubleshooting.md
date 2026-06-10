# MinerU Troubleshooting

Use this guide when `document_to_markdown.py` fails during MinerU upload, polling, result ZIP download, or Markdown extraction. Keep the diagnosis concrete: identify which stage failed before changing the workflow.

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

## Clash Verge Rev / TUN / Fake-IP Pattern

Known symptom:

- MinerU task submission and polling complete.
- Downloading the result from `cdn-mineru.openxlab.org.cn` fails with SSL EOF, TLS handshake failure, or repeated retry exhaustion.
- Local DNS returns a fake-ip range such as `198.18.0.x`.

This usually points to proxy/fake-ip handling of the CDN host, not an SSH configuration issue. `.ssh/config` is unrelated unless the failed command is actually using SSH.

Recommended sequence:

1. Set `HTTPS_PROXY` (or `HTTP_PROXY`) in your shell profile so the script auto-detects the proxy. For example, in PowerShell:

```powershell
$env:HTTPS_PROXY = "http://127.0.0.1:7899"
```

Or in bash/zsh:

```bash
export HTTPS_PROXY=http://127.0.0.1:7899
```

Alternatively, pass `--proxy http://127.0.0.1:7899` on the command line.

2. If the CDN host still fails, resolve the real CDN IP through a trusted resolver outside fake-ip DNS, then pass it explicitly:

```powershell
--resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

3. Keep TLS SNI as the original hostname. The helper does this automatically when `--resolve` is used with `--proxy`.

4. Do not replace this with a silent fallback unless the user has authorized fallback behavior. Report the exact failed stage and the command attempted.

## Diagnostic Commands

Check local proxy listeners:

```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalAddress -in @("127.0.0.1","0.0.0.0") -and $_.LocalPort -in 7897,7898,7899,9090,9097 } | Select-Object LocalAddress,LocalPort,OwningProcess
```

Check whether DNS is returning fake-ip:

```powershell
Resolve-DnsName cdn-mineru.openxlab.org.cn
```

A `198.18.0.x` result is expected in many TUN/fake-ip setups and can explain why direct TLS fails.

Check basic proxy connectivity:

```powershell
curl.exe -x http://127.0.0.1:7899 https://www.baidu.com/ -I
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
| Result ZIP SSL EOF | CDN download | Use `--proxy http://127.0.0.1:7899`; add `--resolve` if fake-ip persists |
| ZIP downloads but no `full.md` | Extraction/output | Inspect `manifest.json` and extracted files before summarizing |

## Current Known Good Pattern

With `HTTPS_PROXY` set (recommended):

```powershell
python .\scripts\document_to_markdown.py "D:\projects\finance\.tmp\pdf-debug\nanrui.pdf" --out-dir "D:\projects\finance\.tmp\agent\document-markdown" --ocr --language ch --timeout 1200 --interval 5 --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

With explicit `--proxy`:

```powershell
python .\scripts\document_to_markdown.py "D:\projects\finance\.tmp\pdf-debug\nanrui.pdf" --out-dir "D:\projects\finance\.tmp\agent\document-markdown" --ocr --language ch --timeout 1200 --interval 5 --proxy http://127.0.0.1:7899 --resolve cdn-mineru.openxlab.org.cn=8.222.80.133,8.222.82.255
```

Prefer HTTP(S) proxy URLs for this helper. Pass `--proxy ""` to disable proxy even when `HTTPS_PROXY` is set.

## Reporting Standard

When conversion still fails, report:

- Input path or URL.
- Whether local validation passed.
- Whether upload, polling, result download, and extraction each succeeded.
- MinerU `task_id`, `trace_id`, `err_code`, and `err_msg` when available.
- Proxy and resolve arguments used.
- Whether a fallback was authorized by the user.
