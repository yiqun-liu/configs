# Neovim config

A `vim.pack`-based Neovim 0.12 config. Built bottom-up: one plugin per file
under `plugin/`, every line intentional and testable in isolation. Design
details and line-level rationale live in the source comments; this file is
the index and the memo-tables.

## Why

- Neovim 0.12 ships `vim.pack` — no third-party plugin manager to bootstrap.
- The previous config accumulated tutorial copy-paste and orphaned plugins
  (`codecompanion`, `minuet-ai` in the lockfile but no config). This rewrite
  keeps only what's used.
- `vim.pack` is intentionally minimal: no TUI, no dependency graph, no opts
  merging. Each plugin is a self-contained file.

## Layout

```
nvim/
├── init.lua              # options + keymaps + git_scheme (no plugins)
├── lua/
│   └── tools/
│       └── config.lua    # shared module: git_scheme + github_url() helper
├── plugin/               # auto-sourced by Neovim at startup, alphabetically
│   ├── treesitter.lua    # nvim-treesitter (main) + FileType autocmd → vim.treesitter.start
│   ├── lspconfig.lua     # nvim-lspconfig + clangd/pylsp/rust_analyzer + LspAttach keymaps
│   ├── luasnip.lua       # LuaSnip + PackChanged build hook (jsregexp)
│   ├── cmp.lua           # nvim-cmp + 5 sources
│   ├── bufferline.lua    # nvim-web-devicons + bufferline (deps grouped)
│   ├── telescope.lua     # plenary + telescope (deps grouped)
│   └── toggleterm.lua    # floating terminal
```

`vim.pack` writes a lockfile (`nvim-pack-lock.json`) at the deployed config
dir at runtime; it is not part of the repo source (deploy is `copy`, so the
lockfile lives at `~/.config/nvim/` only). See
[vim.pack quick reference](#vimpack-quick-reference).

## Design decisions

- **`plugin/*.lua`, not `lua/plugins/*.lua`.** Neovim auto-sources
  `plugin/**/*.lua` at startup (step 11, `:h initialization`), alphabetically.
  `vim.pack.add()` defaults to `load = true` when called from there, so
  plugins load fully without extra ceremony — replacing lazy.nvim's
  spec-discovery with Neovim's own runtime behavior.
- **No number prefixes on files.** Dependencies are resolved by grouping
  related plugins in the same `vim.pack.add` call (e.g. `bufferline.lua`
  adds `nvim-web-devicons` then `bufferline.nvim` in order) rather than
  relying on cross-file load order.
- **`nvim-treesitter` `main` branch.** The new `main` branch is a thin parser
  installer around `tree-sitter-cli`; the engine (`vim.treesitter`) is built
  into Neovim. We add the plugin via `vim.pack.add` and start highlighting
  ourselves via a `FileType` autocmd calling `vim.treesitter.start()`.
- **Built-in catppuccin.** Catppuccin ships with Neovim (since 0.10) — no
  plugin install. Set in `init.lua` right after `termguicolors = true`.

## Prerequisites

Cross-platform (Linux / macOS / Windows). Install on each machine.

### Build / runtime tools

| Tool | Linux | macOS | Windows |
|---|---|---|---|
| Neovim 0.12+ | distro pkg | `brew install neovim` | `winget install Neovim.Neovim` |
| git | distro pkg | `brew install git` | `winget install Git.Git` |
| C compiler | `gcc` / `clang` | Xcode CLT (`xcode-select --install`) | VS Build Tools ("Desktop development with C++") |
| `tree-sitter-cli` ≥ 0.26.1 | `apt install tree-sitter-cli` / `pacman -S tree-sitter-cli` | `brew install tree-sitter-cli` | `winget install tree-sitter.tree-sitter-cli` / `choco install tree-sitter` / `scoop install main/tree-sitter` |

`tree-sitter-cli` compiles parsers cross-platform (`.so`/`.dylib`/`.dll`,
MSVC vs gcc auto-detected).

### Language servers

Install only for languages you edit. Per-server notes in
[LSP server notes](#lsp-server-notes).

| Server | Languages | Install |
|---|---|---|
| `clangd` | C, C++, Obj-C/C++ | Linux: `apt install clangd` / `pacman -S clang` · macOS: `brew install llvm` · Windows: `winget install LLVM.LLVM` |
| `python-lsp-server[all]` | Python | `uv tool install 'python-lsp-server[all]'` (recommended) · or `pipx install …` · or `pip3 install --user …` |
| `rust-analyzer` | Rust | `rustup component add rust-analyzer` (install rustup first from <https://rustup.rs>) |

> **The `[all]` extra on `python-lsp-server` is required.** Without it the
> lint plugins (`pyflakes`, `pycodestyle`, `mccabe`, `autopep8`,
> `pydocstyle`, `rope`) aren't installed and pylsp attaches but publishes
> **zero diagnostics** — a silent failure. Verify:
> ```bash
> python3 -c "import pyflakes, pycodestyle; print('ok')"
> ```

## Running

```bash
# Quick test (no deploy). vim.pack installs to ~/.local/share/nvim/site/pack/core/opt/
nvim -u /home/yiqun/code/configs/nvim/init.lua

# Fully isolated A/B against another nvim config (separate data dir):
ln -s /home/yiqun/code/configs/nvim ~/.config/nvim-test
NVIM_APPNAME=nvim-test nvim
#   Config: ~/.config/nvim-test/   Data: ~/.local/share/nvim-test/
```

Deployed via the repo's config manager (see root `README.md`); once deployed
to `~/.config/nvim`, just run `nvim`.

## Reference

`<leader>` is `\` (Neovim default). Change it with `vim.g.mapleader = " "`
near the top of `init.lua`.

### Keymaps

**File & buffer** (`init.lua`, `bufferline.lua`):

| Key | Mode | Action |
|---|:---:|---|
| `<leader>e` | n | netrw file explorer |
| `<leader>config` | n | cd + edit this config's dir (portable via `config_dir`) |
| `<leader>notes` / `<leader>code` | n | cd + edit `~/notes/` / `~/code/` |
| `<leader>rm` | n | delete current file + `:bdelete!` (guarded) |
| `<leader>load` | n | `:bufdo e!` — reload all buffers from disk |
| `<leader>q` | n | `:bdelete` |
| `<C-n>` / `<C-s>` | n | new buffer / save |
| `<leader>cc` | n | toggle colorcolumn (see [EditorConfig](#editorconfig)) |
| `<S-h>` / `<S-l>` | n | prev / next buffer (bufferline cycle) |

Note: `<leader>q` (bdelete) and `<leader>dl` (setloclist, below) are distinct
because `<leader>` is `\`, not `<space>`.

**Window / split** (`init.lua`) — Alt-modified keys replace the `<C-w>` prefix:

| Key | Action |
|---|---|
| `<A-h/j/k/l>` | move to left / down / up / right window |
| `<A-=>` / `<A-->` | taller / shorter |
| `<A-.>` / `<A-,>` | narrower / wider |

**LSP & diagnostics** — Neovim 0.12 built-in defaults (no config needed):

| Key | Mode | Action |
|---|:---:|---|
| `K` | n | hover doc (set on `LspAttach` if unmapped) |
| `grn` / `gra` | n (`gra` also x) | rename / code action |
| `grr` / `gri` / `grt` / `grx` | n | references / implementation / type def / codelens run |
| `gO` | n | document symbols |
| `<C-S>` | i, s | signature help |
| `[d` / `]d` · `[D` / `]D` | n | prev/next · first/last diagnostic |
| `<C-W>d` | n | diagnostic float |
| `[q` / `]q` / `[Q` / `]Q` | n | quickfix nav |
| `omnifunc` / `formatexpr` | — | LSP-backed `Ctrl-X Ctrl-O` / `gq` |

Our additions (`plugin/lspconfig.lua`):

| Key | Mode | Action | Why |
|---|:---:|---|---|
| `gd` / `gD` | n (buf) | definition / declaration | not defaults (vim's native are regex searches); buffer-local so native still work in non-LSP buffers |
| `[d` / `]d` | n | prev/next diagnostic **+ auto-float** | overrides default to pop the float (preserves count: `3]d` jumps 3) |
| `<leader>dl` | n | setloclist with all buffer diagnostics | defaults only navigate a list |

Telescope LSP variants (`plugin/telescope.lua`, screen-aware split):

| Key | Action |
|---|---|
| `<leader>gd` | definitions in smart-split (vsplit if wide, split if tall) |
| `<leader>grr` | references in smart-split |

Convention: `<leader>{keys}` = smart-split version of the in-place `{keys}`
action. Format whole buffer: `gggqG` (default `gq` via LSP `formatexpr`) or
`:lua vim.lsp.buf.format()`.

**Completion** (`plugin/cmp.lua`) — INSERT-mode custom mappings:

| Key | Action |
|---|---|
| `<C-l>` | trigger completion menu (replaces `<C-Space>` — IME conflict) |
| `<CR>` | confirm (`select=true`: picks first if none highlighted) |
| `<Tab>` / `<S-Tab>` | next / prev item, **or** snippet expand/jump (LuaSnip-aware; works in i+s) |

Preset defaults (`<C-n>`/`<C-p>`/`<C-y>`/`<C-e>`) and cmdline (`:`/`/`/`?`)
completion use `cmp.mapping.preset.*` — see `:h cmp`. In NORMAL mode, use
`K` for LSP hover (not a completion key).

**Fuzzy finder** (`plugin/telescope.lua`):

| Key | Action |
|---|---|
| `<leader>ff` / `<leader>fg` / `<leader>fb` / `<leader>fh` | find files / live grep / buffers / help tags |
| `<C-p>` | find files (alias; overrides redundant `k`) |
| `<C-g>` | find git-tracked files |
| `<leader>grep` | live grep (alias) |

**Terminal** (`plugin/toggleterm.lua`):

| Key | Action |
|---|---|
| `<c-\>` | toggle floating shell |

### Commands

| Command | Purpose |
|---|---|
| `:TSInstall cpp rust python …` | install parsers (calls `tree-sitter build` internally) |
| `:TSInstall! {lang…}` | force reinstall (after upgrading the plugin) |
| `:TSUpdate [{lang…}]` | update parsers (no args = all); shows what would update first |
| `:TSUninstall {lang…}` | remove parsers |
| `:lua =vim.pack.get()` | list managed plugins |
| `:packupdate` / `:lua vim.pack.update()` | update plugins (opens confirmation buffer) |
| `:write` / `:quit` | in confirmation buffer: apply / discard |
| `:lua =vim.lsp.get_clients({ bufnr = 0 })` | inspect LSP clients on current buffer (`:LspInfo` is not registered on nvim-lspconfig `master`) |
| `:colorscheme` / `:set number? mouse?` / `:messages` | active scheme / option values / startup errors |

Update parsers after a Neovim major bump (parser ABI may change) or when
hitting a highlight bug fixed in a newer grammar. Folding uses the
tree-sitter tree (`foldmethod=expr`,
`foldexpr=v:lua.vim.treesitter.foldexpr()`); files open with levels 1–3
expanded (fold commands are vim built-ins under the `z` prefix — see
`:h fold-commands`).

### Colorscheme

Default: `catppuccin` (built-in since Neovim 0.10). Set in `init.lua` after
`termguicolors = true`. Two variants via `'background'`:

| `background` | Variant |
|---|---|
| `dark` (default) | Mocha |
| `light` | Latte |

Switch at runtime: `:set background=light`. Try other built-ins:
`:colorscheme <Tab>` or `:Telescope colorscheme` (`<CR>` applies). Modern
built-ins worth trying: `habamax`, `lunaperche`, `quiet`, `sorbet`,
`unokai` (`ls /usr/share/nvim/runtime/colors/` for the full list).

### EditorConfig

Neovim's built-in EditorConfig plugin is enabled by default. This config
adds **EditorConfig-aware `colorcolumn`**: if a project's `.editorconfig`
sets `max_line_length = N`, the guide appears at column N; otherwise falls
back to 100. Resolved by working directory (the `.editorconfig` above the
opened file), not per-file.

| Scenario | `colorcolumn` |
|---|---|
| `.editorconfig` with `max_line_length = 80` | `"80"` |
| `.editorconfig` without `max_line_length` | `"100"` |
| No `.editorconfig` | `"100"` |

Neovim's EditorConfig handler maps `max_line_length` to `textwidth` (enables
auto-wrap). Our `FileType`/`BufEnter` autocmds read `b:editorconfig.max_line_length`
directly and set `colorcolumn` only — they do **not** touch `textwidth`. To
disable auto-wrap, add `vim.opt.formatoptions:remove('t')` to `init.lua`.
Toggle the guide with `<leader>cc`; `:set colorcolumn=` disables.

### Git scheme (SSH vs HTTPS)

Set in `init.lua`: `require('tools.config').git_scheme = 'https'` (or `'ssh'`).

| Scheme | When |
|---|---|
| `https` (default) | works everywhere, no key needed |
| `ssh` | GitHub SSH keys configured (faster auth, no rate limits) |

Applies only to `vim.pack.add()` calls we author (where `src` is
`require('tools.config').github_url('foo/bar')`). Does **not** apply to
`:TSInstall`/`:TSUpdate` (nvim-treesitter fetches parsers via curl HTTPS
from a hardcoded URL list — not git, no SSH option) or third-party plugins'
internal git/curl.

When switching scheme + `:restart`, `vim.pack` detects the `src` mismatch
(lockfile vs `init.lua`), deletes the old clone, re-clones with the new URL;
the lockfile updates on the next `vim.pack.add()`. With `'ssh'` and no key
configured, clones fail with a git auth error — `vim.pack` uses libuv spawn
(no TTY), so git won't prompt, it just fails. Pick `'https'` if unsure.

## Plugin inventory

**Kept** (no built-in equivalent, no clear successor):

| Plugin | Used for |
|---|---|
| `nvim-treesitter` (main) | parser installer for built-in `vim.treesitter` |
| `nvim-lspconfig` | LSP server configs (used by `vim.lsp.config`) |
| `nvim-cmp` + 5 sources | completion (0.12's `vim.lsp.completion` lacks snippets/path/buffer) |
| `LuaSnip` + `cmp_luasnip` | snippet engine; bridge into nvim-cmp |
| `telescope.nvim` + `plenary.nvim` | fuzzy finder + its dependency |
| `bufferline.nvim` + `nvim-web-devicons` | buffer tabline + its icon dependency |
| `toggleterm.nvim` | floating terminal |

**Dropped** (replaced by built-in or unused):

| Plugin | Reason |
|---|---|
| `lazy.nvim` | replaced by built-in `vim.pack` |
| `catppuccin` (plugin) | declared but colorscheme call was commented out — built-in catppuccin used instead |
| `codecompanion.nvim` / `minuet-ai.nvim` | lockfile only, no config — orphans |

## vim.pack quick reference

Plugin spec forms:

```lua
vim.pack.add({
  'https://github.com/user/plugin',                                -- bare string
  { src = 'https://github.com/user/plugin', name = 'foo' },         -- table form
  { src = 'https://github.com/user/plugin', version = 'main' },     -- branch
  { src = 'https://github.com/user/plugin', version = 'v1.0' },     -- tag
  { src = 'https://github.com/user/plugin', version = vim.version.range('1.0') }, -- semver range
})
```

Lifecycle:

| Aspect | Detail |
|---|---|
| Install dir | `stdpath('data')/site/pack/core/opt/<name>` |
| Lockfile | `nvim-pack-lock.json` at `stdpath('config')` — generated at runtime, machine-local (not in repo source) |
| `load` option | `true` = `:packadd` (source `plugin/` + `ftdetect/`); `false` = `:packadd!` (rtp only); `function` = custom |
| Default `load` | `false` during `init.lua` sourcing; `true` elsewhere (incl. `plugin/*.lua`) |
| Build hooks | `PackChangedPre` / `PackChanged` autocommands; filter by `ev.data.spec.name` and `ev.data.kind` ∈ `{install, update, delete}` |

## LSP server notes

Three servers enabled in `plugin/lspconfig.lua`; each attaches
automatically by filetype.

| Server | Languages | Status |
|---|---|---|
| `clangd` | C, C++, Obj-C/C++ | official (LLVM project) |
| `pylsp` | Python | community fork of Microsoft's `pyls` |
| `rust-analyzer` | Rust | official (Rust project) |

### clangd (C/C++)

Reads `compile_commands.json` (recommended) or `compile_flags.txt` from the
project root (or any parent of the opened file) for include paths and flags.
Without either, clangd still parses with defaults and catches syntax/type
errors, but `#include <foo.h>` may flag as unresolved.

```bash
cmake -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
ln -sf build/compile_commands.json .   # clangd searches upward from the source file
```

### rust-analyzer (Rust)

Works out of the box with any `cargo`-based project — no per-project config.
Installed via `rustup component add rust-analyzer` on all platforms.

### pylsp (Python)

**Concept — two Python environments, one for the linter, one for the project:**

| Env | What lives here | Used for |
|---|---|---|
| **(A) pylsp's own env** | `python-lsp-server` + lint plugins (`pyflakes`, `pycodestyle`, `mccabe`, `autopep8`, `pydocstyle`, `rope`) + `jedi` completion | always — the running server process |
| **(B) the project's `.venv/`** (`uv sync`, `python -m venv`, …) | whatever the project depends on (`requests`, `numpy`, your own code) | import resolution — "does `import foo` resolve?" |

pylsp is **not** installed in each uv project — install it once globally
(see [Prerequisites → Language servers](#language-servers)).

**What needs env (B), and what doesn't:**

- **Static-only checks** (unused import, undefined name, line length,
  trailing whitespace): run in env (A) from the file's AST — never execute
  your code. Work even if env (B) doesn't exist.
- **Completion / go-to-definition of third-party packages** (e.g.
  `import requests` → `requests.get(...)`): `jedi` follows the import into
  the package's source, which lives in env (B). Without env (B), no
  completion for `requests.get`, and `gd` on `requests` won't jump.

**How pylsp finds the project's `.venv/` — `jedi` resolution order:**

1. Explicit `pylsp.plugins.jedi.environment` (absolute path to a Python
   interpreter).
2. The `VIRTUAL_ENV` env var (set by `source .venv/bin/activate`,
   `.venv\Scripts\activate`, or `uv run …`).
3. Fallback: the interpreter running pylsp itself (system Python) — won't
   see project-only packages.

Three common ways to give pylsp access to your uv project's venv:

**Option 1 — `uv run nvim <file>`** (lightest; ad-hoc edits). uv sets
`VIRTUAL_ENV` for the child process, so jedi picks up the project's
`.venv/` automatically:

```bash
cd ~/code/myproject
uv sync                       # ensure .venv/ exists
uv run nvim src/mypkg/main.py
```

**Option 2 — activate before nvim** (works with any venv, not just uv):

```bash
source .venv/bin/activate     # Windows: .venv\Scripts\activate
nvim src/mypkg/main.py
```

**Option 3 — explicit `jedi.environment`** (most deterministic; pinned
per-project via `.pylsp.toml`, dropped in the project root — pylsp reads it
automatically when it lives above any opened Python file):

```toml
# .pylsp.toml
[plugins.jedi]
environment = ".venv/bin/python"   # Windows: .venv\\Scripts\\python.exe
```

**TL;DR:** one global `python-lsp-server[all]` covers all projects; for
ad-hoc edits `uv run nvim file.py` is the lightest path to project-aware
completion; forgetting `[all]` = silent zero-diagnostics (verify with
`python3 -c "import pyflakes, pycodestyle"`).
