-- plugin/treesitter.lua — syntax highlighting & folding via tree-sitter.
--
-- Tree-sitter is a parsing framework that builds a real syntax tree of
-- your code (not just regex-based highlighting). Neovim ships with
-- built-in tree-sitter support (`vim.treesitter.start`); the
-- nvim-treesitter plugin's `main` branch is just a PARSER INSTALLER —
-- it provides `:TSInstall` to download prebuilt parsers (one `.so` file
-- per language) and `:TSUpdate` to refresh them.
--
-- We use the `main` branch (NOT `master`) because `main` is the
-- modern branch that works with the built-in `vim.treesitter.start`
-- API. The legacy `master` branch has its own setup() with a different
-- API; we don't want that.
--
-- How highlighting works at runtime:
--   1. User opens a file.
--   2. Neovim detects the filetype (e.g. 'cpp').
--   3. Our FileType autocmd (below) calls `vim.treesitter.start(buf)`.
--   4. Neovim tries to load the parser for that language.
--   5. If a parser is installed (e.g. via `:TSInstall cpp`), highlighting
--      and folding turn on. If not, `start` raises an error and our
--      `pcall` swallows it silently — the file just opens without
--      tree-sitter, no harm done.

local config = require('tools.config')

-- Install nvim-treesitter. On first run this clones the repo; on
-- subsequent runs it just adds the path to rtp.
vim.pack.add({
  { src = config.github_url('nvim-treesitter/nvim-treesitter'), version = 'main' },
})

-- Create an augroup to hold our FileType autocmd. Using an augroup
-- with `clear = true` means: "delete any existing autocmds in this
-- group, then start fresh." This makes the file safe to re-source
-- (e.g. via `:source %` while editing it) — without the group, every
-- re-source would ADD another copy of the autocmd, and they'd pile up.
vim.api.nvim_create_augroup('TreesitterStart', { clear = true })

-- Register an autocmd that fires whenever Neovim sets a buffer's
-- filetype (which happens once per buffer, after the file is read).
--
-- `group` attaches this autocmd to the augroup we just made.
-- `args.buf` is the buffer number that triggered the event.
vim.api.nvim_create_autocmd('FileType', {
  group = 'TreesitterStart',
  desc = 'Start built-in tree-sitter highlighter if parser available',
  callback = function(args)
    -- Try to start tree-sitter on this buffer. `pcall` (protected
    -- call) catches any error and returns (false, err); on success
    -- it returns (true, nil). We discard the error — a missing parser
    -- is normal and not worth bothering the user about.
    local ok = pcall(vim.treesitter.start, args.buf)
    if not ok then return end

    -- If tree-sitter started successfully, also enable tree-sitter
    -- based FOLDING on every window currently showing this buffer.
    -- (A buffer can be visible in multiple windows simultaneously —
    -- e.g. after a split — so we loop through all windows.)
    for _, win in ipairs(vim.api.nvim_list_wins()) do
      if vim.api.nvim_win_get_buf(win) == args.buf then
        -- `vim.wo[win]` is window-local option access scoped to a
        -- specific window. `foldmethod = 'expr'` tells Neovim to
        -- compute fold levels by evaluating `foldexpr` for each line.
        -- `v:lua.vim.treesitter.foldexpr()` is the built-in function
        -- that uses the tree-sitter syntax tree to decide where
        -- folds go (e.g. fold a whole function body).
        vim.wo[win].foldexpr = 'v:lua.vim.treesitter.foldexpr()'
        vim.wo[win].foldmethod = 'expr'
      end
    end
  end,
})
