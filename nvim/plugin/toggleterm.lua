-- plugin/toggleterm.lua — floating/terminal toggle management.
--
-- Toggleterm lets you spawn terminals inside Neovim (as floating
-- windows, splits, or full-screen). We use it for one keymap:
--   - <c-\> : toggle a generic floating shell (for quick commands)
--
-- To run a specific command (htop, btop, lazygit, etc.) inside a
-- floating terminal, use `:TermExec cmd="..."` after toggling — or
-- define a dedicated `Terminal:new(...)` instance here if you want
-- a one-key binding for a specific tool.

local config = require('tools.config')

vim.pack.add({
  { src = config.github_url('akinsho/toggleterm.nvim'), version = 'main' },
})

-- Configure toggleterm itself:
--   open_mapping = [[<c-\>]]  -- which key toggles the terminal.
--     Lua's [[...]] long-bracket string avoids escape-char escaping.
--   direction = 'float'        -- terminals open as floating windows.
--   float_opts.border = 'curved'  -- rounded-corner border style.
--   float_opts.winblend = 30   -- 0=opaque, 100=fully transparent.
--     30 gives a subtle see-through effect so you can tell what's
--     underneath the floating terminal.
require('toggleterm').setup({
  open_mapping = [[<c-\>]],
  direction = 'float',
  float_opts = {
    border = 'curved',
    winblend = 30,
  },
})
