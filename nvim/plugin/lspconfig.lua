-- plugin/lspconfig.lua — Language Server Protocol (LSP) configuration.
--
-- LSP is the protocol VSCode popularized: a language server (like
-- clangd for C/C++, pylsp for Python, rust-analyzer for Rust) runs as
-- a separate process, reads your code, and tells the editor about
-- errors, definitions, references, completions, etc. Neovim 0.12 has
-- a built-in LSP client (`vim.lsp`); the nvim-lspconfig plugin just
-- provides sensible default configs for ~200 language servers.
--
-- This file:
--   1. Installs nvim-lspconfig.
--   2. Enables three language servers (clangd, pylsp, rust_analyzer).
--   3. Adds diagnostic keymaps NOT covered by Neovim 0.11+ defaults
--      (modified [d/]d with auto-float; <leader>dl for setloclist).
--   4. Adds buffer-local LSP keymaps NOT covered by Neovim 0.11+
--      defaults — only `gd`/`gD` (definition/declaration), since
--      vim's native `gd`/`gD` are regex-based and we want semantic
--      LSP jumps. Other LSP keymaps (hover, rename, code action,
--      references, etc.) come from Neovim 0.12's built-in defaults.

local config = require('tools.config')

vim.pack.add({
  { src = config.github_url('neovim/nvim-lspconfig'), version = 'master' },
})

-- Configure each language server with an empty options table. This is
-- NOT a no-op: `vim.lsp.config(name, {})` MERGES {} with the default
-- config that nvim-lspconfig ships in `lsp/<name>.lua`. So we get the
-- sensible defaults (command to launch the server, filetypes it
-- handles, root directory detection) without overriding anything.
--
-- To override a default, you'd pass e.g.:
--   vim.lsp.config('clangd', { cmd = { 'clangd', '--background-index' } })
vim.lsp.config('clangd', {})
vim.lsp.config('pylsp', {})
vim.lsp.config('rust_analyzer', {})

-- Actually enable the servers. From this point on, when Neovim opens a
-- file whose filetype matches a server's registered filetypes, it
-- launches the server in the background and attaches it to the buffer.
vim.lsp.enable({ 'clangd', 'pylsp', 'rust_analyzer' })

-- ============================================================================
-- Global diagnostic keymaps not covered by Neovim 0.11+ defaults.
--
-- Neovim 0.12's built-in defaults (set automatically at startup) provide:
--   [d / ]d           — jump prev/next diagnostic (respects count, no float)
--   [D / ]D           — jump first/last diagnostic
--   <C-W>d            — open diagnostic float at cursor
--   [q / ]q / [Q / ]Q — quickfix list navigation (vim-unimpaired style)
--
-- We override [d / ]d to AUTO-POP the float (clearer UX — you see the
-- message without an extra keystroke), preserving the count (e.g. `3]d`
-- jumps 3 diagnostics forward). We also add <leader>dl to FILL the
-- location list with all buffer diagnostics — defaults only navigate an
-- existing list, they don't populate it from current diagnostics.
-- ============================================================================

-- `[d` / `]d` jump to previous / next diagnostic AND auto-pop the float.
-- Wrapped in Lua closures so we can pass options:
--   count = ±vim.v.count1  — how many diagnostics to skip; respects
--                            vim's `[count]` (e.g. `3]d` jumps 3 forward;
--                            default count = 1)
--   float = true           — also pop up the float for the jumped-to diag
--
-- We use `vim.diagnostic.jump` (the modern API, Neovim 0.11+) instead
-- of the older `vim.diagnostic.goto_prev`/`goto_next`, which are
-- deprecated since 0.11 and scheduled for removal.
vim.keymap.set('n', '[d', function()
  vim.diagnostic.jump({ count = -vim.v.count1, float = true })
end)
vim.keymap.set('n', ']d', function()
  vim.diagnostic.jump({ count = vim.v.count1, float = true })
end)

-- `<leader>dl` populates the location list with all diagnostics in the
-- current buffer. Mnemonic: d-iagnostics, l-ist. After populating,
-- navigate with the default `[q` / `]q` (next/prev) or `[Q` / `]Q`
-- (first/last). `:lopen` opens the list window; `:lclose` closes it.
--
-- "Location list" is vim's per-window quickfix-style list (vs. the
-- global quickfix list `:copen`).
vim.keymap.set('n', '<leader>dl', vim.diagnostic.setloclist)

-- ============================================================================
-- Buffer-local LSP keymaps (only what Neovim 0.11+ defaults DON'T cover).
--
-- Neovim 0.12's built-in defaults provide (set automatically on LspAttach):
--   K               — hover doc popup (only if K isn't already mapped
--                     AND keywordprg is at its default value)
--   grn             — rename symbol
--   gra             — code action (normal + visual)
--   grr             — list references
--   gri             — go to implementation
--   grt             — go to type definition
--   grx             — codelens run
--   gO              — document symbols outline
--   <C-S> (insert)  — signature help
--   omnifunc        — LSP-backed omni-completion (Ctrl-X Ctrl-O)
--   formatexpr      — LSP-backed `gq` motion for formatting
--
-- We add only `gd` and `gD` — vim's native `gd`/`gD` are regex-based
-- "find word under cursor in function/global scope"; for LSP-attached
-- buffers we want semantic jump-to-definition instead. Note these are
-- buffer-local (scoped via `buf = ev.buf`), so vim's native `gd`/`gD`
-- still work in non-LSP buffers (e.g. plain text).
--
-- Format the whole buffer with `gggqG` (default `gq` motion via the
-- LSP-backed `formatexpr` above), or run `:lua vim.lsp.buf.format()<CR>`
-- as a one-off Ex command.
-- ============================================================================

vim.api.nvim_create_autocmd('LspAttach', {
  desc = 'Buffer-local LSP keymaps (additions to Neovim 0.11+ defaults)',
  callback = function(ev)
    -- `buf = ev.buf` scopes each keymap below to THIS buffer only.
    -- Keymaps appear/disappear automatically as LSP servers
    -- attach/detach — no leakage to non-LSP buffers, so vim's native
    -- `gd`/`gD` (regex local/global declaration search) still work
    -- in non-LSP buffers.
    local opts = { buf = ev.buf }

    -- Go to definition / declaration. Uppercase = stronger variant
    -- (vim convention: lowercase = common case, uppercase = rarer
    -- variant). In most languages `gd` and `gD` go to the same place;
    -- in C/C++/Java they can differ (forward declaration vs definition).
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)   -- go to DEFINITION
    vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, opts)  -- go to DECLARATION
  end,
})
