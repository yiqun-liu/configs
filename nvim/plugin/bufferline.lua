-- plugin/bufferline.lua — tabline UI for open buffers.
--
-- Files under `plugin/` are auto-sourced by Neovim at startup (after
-- init.lua), in ALPHABETICAL order. So this file runs after init.lua
-- but before cmp.lua, lspconfig.lua, etc. Each plugin/*.lua is a
-- self-contained "load this plugin + configure it" unit.
--
-- This file loads TWO plugins in one `vim.pack.add` call:
--   1. nvim-web-devicons — provides file-type icons (the little glyphs
--      next to file names). bufferline depends on these.
--   2. bufferline.nvim   — the actual tabline UI.
--
-- Grouping a dependency (devicons) with its consumer (bufferline) in
-- the same `vim.pack.add` call avoids the cross-file load-order
-- problem: both plugins are on the runtimepath before we call
-- `require('bufferline').setup()`.

-- Grab our shared config helper so we can build a clone URL.
-- `require('tools.config')` returns the singleton table from
-- lua/tools/config.lua.
local config = require('tools.config')

-- `vim.pack.add` is Neovim 0.12's built-in plugin manager. It:
--   - Clones each plugin under ~/.local/share/nvim/site/pack/core/opt/
--   - Adds its path to the runtimepath so its lua/ is require-able
--   - Writes a lockfile (nvim-pack-lock.json) so installs are repeatable
-- On subsequent startups, if the plugin is already cloned and the
-- lockfile matches, `vim.pack.add` skips the network and just adds
-- the existing path to rtp (fast).
--
-- `version = 'main'` (or 'master') tells vim.pack which branch to track.
-- Each repo has its own default branch name; check GitHub to see which.
vim.pack.add({
  { src = config.github_url('nvim-tree/nvim-web-devicons'), version = 'master' },
  { src = config.github_url('akinsho/bufferline.nvim'),   version = 'main' },
})

-- Require bufferline ONCE and assign to a local. The returned table
-- (type: table) contains setup(), cycle(), go_to(), etc. We reuse the
-- same local for both setup and the keymaps below — no need to require
-- twice (require caches anyway, but one call is cleaner to read).
local bufferline = require('bufferline')

-- Run bufferline's setup with an empty options table. Passing `{}` means
-- "use bufferline's built-in defaults" — bufferline's defaults are
-- sensible, so we don't need to override anything here.
bufferline.setup({})

-- Define the <S-h>/<S-l> "previous/next buffer" keymaps here (instead
-- of in init.lua) so they use bufferline's cycle function.
--
-- Why this matters: bufferline lets the user sort, pin, and drag
-- buffers into a custom order. Vim's built-in `:bprev`/`:bnext` walk
-- the buffer STACK (creation order), which desyncs from bufferline's
-- sorted order — pressing <S-l> would jump to a "different" buffer
-- than the one highlighted as "next" in the tabline. Using
-- `bufferline.cycle(±1)` keeps the tabline and the keymap in sync.
--
-- We pass a Lua function (not a string command) as the RHS so we can
-- call `bufferline.cycle` directly. Wrapping it in `function() ... end`
-- instead of passing `bufferline.cycle` bare lets us pre-bind the
-- argument (-1 or 1) — otherwise we'd have to pass the arg each call.
vim.keymap.set('n', '<S-h>', function() bufferline.cycle(-1) end)  -- Shift-H = previous
vim.keymap.set('n', '<S-l>', function() bufferline.cycle(1) end)   -- Shift-L = next
