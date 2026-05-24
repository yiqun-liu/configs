# Document to Markdown Skill

This skill converts documents to LLM-friendly Markdown. The current backend is MinerU, and the helper script reads the backend API token from an environment variable named `MINERU_TOKEN`; do not store the token in this repository.

## Windows Token Setup

PowerShell session only:

```powershell
$env:MINERU_TOKEN = "your-token-here"
```

Persistent user environment variable:

```powershell
[Environment]::SetEnvironmentVariable("MINERU_TOKEN", "your-token-here", "User")
```

Open a new terminal after setting the persistent variable, then verify:

```powershell
echo $env:MINERU_TOKEN
```

PowerShell profile, similar to a Unix `.bashrc`:

```powershell
notepad $PROFILE
```

Add this line:

```powershell
$env:MINERU_TOKEN = "your-token-here"
```

Then restart PowerShell or run:

```powershell
. $PROFILE
```

## Unix-like Shell Setup

Bash or Zsh:

```bash
export MINERU_TOKEN="your-token-here"
```

To persist it, add that line to `~/.bashrc`, `~/.zshrc`, or the shell profile used by your agent runtime.

## Example

```powershell
python .\scripts\document_to_markdown.py "D:\docs\paper.pdf" --out-dir ".\.tmp\agent\document-markdown" --ocr
```

The script writes `full.md`, `manifest.json`, and extracted backend result files under the output directory.
