-- init.lua — the entry point Neovim reads when it starts up.
--
-- In a standard Neovim install this file lives at ~/.config/nvim/init.lua
-- and is sourced automatically. We can also load it from anywhere with
-- `nvim -u /path/to/init.lua`, so the first thing we do is put our config
-- directory on the runtimepath (see below) so Neovim can find our `lua/`
-- and `plugin/` subdirectories.

-- Work out the directory this file lives in.
--   debug.getinfo(1, 'S')  -- Lua introspection: info about the
--                          -- currently running chunk (this file).
--                          -- 'S' asks for "what + where".
--   .source                -- a string like "@/path/to/init.lua";
--                          -- the leading '@' marks it as a file name.
--   :sub(2)                -- strip the leading '@'.
--   vim.fn.fnamemodify(..) -- Neovim path helper. ':p:h' means
--                          -- "full Path, then Head" (the parent dir).
local config_dir = vim.fn.fnamemodify(debug.getinfo(1, 'S').source:sub(2), ':p:h')

-- Put our config dir on the runtimepath (rtp) — but ONLY when it isn't
-- already there. Neovim auto-adds `stdpath('config')` to rtp at startup,
-- so:
--   - When deployed as ~/.config/nvim/ (or via NVIM_APPNAME=nvim-pack):
--     stdpath('config') == config_dir, the prepend is redundant, skip it.
--   - When loaded with `nvim -u /path/to/this/init.lua` for testing:
--     stdpath('config') is still ~/.config/nvim/ (the -u flag only changes
--     where init.lua is loaded FROM, not where stdpath points), so
--     config_dir is NOT on rtp and we must prepend it — otherwise
--     require('tools.config') and plugin/*.lua auto-sourcing both fail.
if vim.fn.stdpath('config') ~= config_dir then
  vim.opt.runtimepath:prepend(config_dir)
end

-- Choose the git transport every `vim.pack.add` call below will use.
--   'https' — works everywhere, no key needed (recommended default).
--   'ssh'   — passwordless if your SSH key has no passphrase, but
--             requires an SSH key registered with GitHub.
-- See lua/tools/config.lua for how this value is consumed.
require('tools.config').git_scheme = 'https'

-- ============================================================================
-- Options: editor-wide settings (the same things `:set` changes).
-- Each `vim.opt.X = Y` line is equivalent to typing `:set X=Y`.
-- ============================================================================

vim.opt.mouse = ""               -- disable mouse entirely (keyboard-first)
-- Line numbers: `number` and `relativenumber` are INDEPENDENT options
-- (setting one does NOT affect the other). To turn off ALL line numbers:
-- `:set nonu nornu` — not just `:set nonu`, which leaves relative
-- numbers on. That's a common trap.
vim.opt.number = true           -- show absolute line numbers in the gutter
vim.opt.relativenumber = true   -- show RELATIVE numbers (jumps like 12j become easy)
vim.opt.cursorline = true       -- highlight the line the cursor is on
vim.opt.smartindent = true      -- auto-indent new lines based on the previous line
vim.opt.hlsearch = false        -- don't keep search matches highlighted after search
vim.opt.incsearch = true        -- jump to matches AS you type the search pattern
vim.opt.scrolloff = 8           -- keep at least 8 lines of context above/below cursor
vim.opt.splitright = true       -- new vertical splits open to the RIGHT of current
vim.opt.termguicolors = true    -- enable 24-bit RGB colors (most themes need this)

-- Set the colorscheme to Catppuccin (Latte variant for light background,
-- Mocha variant for dark background). Catppuccin is a built-in Neovim
-- colorscheme (since Neovim 0.10) — contributed to the upstream
-- vim/colorschemes repo by the Catppuccin community, so no plugin
-- install is needed.
--
-- `vim.cmd.colorscheme(name)` is the Lua equivalent of typing
-- `:colorscheme catppuccin`. We set it AFTER `termguicolors = true`
-- because Catppuccin (like most modern schemes) requires 24-bit RGB
-- color support — without `termguicolors`, it falls back to 16-color
-- mode and looks wrong.
--
-- To switch between the two variants:
--   :set background=light   (Latte — light pastel)
--   :set background=dark    (Mocha — dark pastel, the default)
--
-- To try other built-in schemes:
--   :colorscheme <Tab>      (tab-complete available names)
--   :Telescope colorscheme  (fuzzy picker; <CR> applies, no live-preview)
vim.cmd.colorscheme('catppuccin')

-- Folds: start files with levels 1–3 expanded (only deeper nesting folded).
-- Folding itself is enabled by plugin/treesitter.lua, which sets
-- foldmethod='expr' + foldexpr='v:lua.vim.treesitter.foldexpr()'.
-- foldlevelstart = N means "set foldlevel to N when a new buffer opens";
-- folds with level > N are closed, levels 1–N are open.
vim.opt.foldlevelstart = 3

-- Fold display: make folded lines visually striking.
--   foldtext: a vim expression evaluated per fold. Shows a triangle
--   prefix (▸) + the first line of the folded region + line count.
--   fillchars.fold: the character filling remaining space to the right
--   of the fold text. Middle dot (·) is cleaner than the default dash
--   and makes folded lines visually distinct from normal code.
vim.opt.fillchars = { fold = '·' }
vim.opt.foldtext = "printf('▸ %s … %d lines', getline(v:foldstart), v:foldend - v:foldstart + 1)"

-- Built-in fold commands (all start with `z` — think of the horizontal
-- bar in `z` as a paper crease you fold along):
--
--   Lowercase = single fold under cursor:
--     zc  z + c(lose)     — fold (collapse) the fold under cursor
--     zo  z + o(pen)       — unfold (expand) the fold under cursor
--     za  z + a(ll)        — toggle (close→open, open→close)
--
--   Uppercase = entire buffer:
--     zM  z + M(aximum)    — close ALL folds (maximum folding)
--     zR  z + R(educe)     — open ALL folds (reduce folding to zero)
--
--   Level-based (less common):
--     zm  z + m(ore)       — fold one more level (close deeper)
--     zr  z + r(educe)     — fold one less level (open one level)

-- ============================================================================
-- Colorcolumn: visual guide line at a configurable column.
-- ============================================================================
-- Default: column 100. Override per-project via .editorconfig
-- (max_line_length property). Toggle interactively with <leader>cc
-- or :set colorcolumn=N.
--
-- Note: EditorConfig settings are resolved from the .editorconfig file
-- in the file's parent directory tree — the colorcolumn reflects the
-- project's editorconfig (by working directory), not a per-file manual
-- setting. colorcolumn is window-local; the BufEnter autocmd below
-- updates it when switching between buffers in the same window.

vim.opt.colorcolumn = "100"

-- Shared logic: read b:editorconfig.max_line_length and set colorcolumn.
-- Falls back to "100" when no .editorconfig or no max_line_length.
-- Does NOT set textwidth (no auto-wrap — visual guide only).
local function set_colorcolumn(buf)
  local ec = vim.b[buf].editorconfig
  if ec and ec.max_line_length and ec.max_line_length ~= 'off' then
    vim.wo.colorcolumn = tostring(ec.max_line_length)
  else
    vim.wo.colorcolumn = '100'
  end
end

vim.api.nvim_create_augroup('EditorConfigCC', { clear = true })

-- FileType: fires when a file is opened and its filetype detected.
-- editorconfig's own FileType autocmd populates b:editorconfig; our
-- vim.schedule defers until after that runs.
vim.api.nvim_create_autocmd('FileType', {
  group = 'EditorConfigCC',
  desc = 'Set colorcolumn from editorconfig max_line_length',
  callback = function(args)
    vim.schedule(function() set_colorcolumn(args.buf) end)
  end,
})

-- BufEnter: fires when switching to a different buffer in the same
-- window. Without this, colorcolumn would "stick" from the first file
-- opened in that window.
vim.api.nvim_create_autocmd('BufEnter', {
  group = 'EditorConfigCC',
  desc = 'Update colorcolumn on buffer switch',
  callback = function(args)
    vim.schedule(function() set_colorcolumn(args.buf) end)
  end,
})

-- Toggle colorcolumn on/off. Useful when the guide is distracting
-- (e.g. reading wide documentation). Also changeable via Ex commands:
--   :set colorcolumn=80  (column 80)
--   :set colorcolumn=    (disable)
vim.keymap.set('n', '<leader>cc', function()
  vim.wo.colorcolumn = (vim.wo.colorcolumn == '') and '100' or ''
end)

-- ============================================================================
-- Keymaps: custom shortcuts.
-- <leader> is a special prefix key (backslash by default). It namespaces
-- custom keymaps so they don't shadow built-in ones.
-- ============================================================================

-- netrw (Neovim's built-in file explorer) and directory shortcuts.
--
-- vim.cmd.Ex is the function form of `:Ex` — opens netrw in the
-- current window. Passing a function reference (not a string) as the
-- RHS lets Neovim call it directly when the key is pressed.
vim.keymap.set('n', '<leader>e', vim.cmd.Ex)

-- `<leader>config` jumps to this config's directory so you can edit it
-- quickly. We use the `config_dir` local from the top of the file —
-- this makes the keymap portable (it points at wherever init.lua lives,
-- not a hardcoded `~/.config/nvim/`).
vim.keymap.set('n', '<leader>config', function()
  vim.cmd.cd(config_dir)   -- `:cd` to the config dir (changes :pwd)
  vim.cmd.e(config_dir)    -- `:e` the dir — since it's a directory, netrw opens
end)

-- The next two are convenience shortcuts for jumping to common work
-- directories. They use the `<cmd>...<cr>` form: a keymap RHS string
-- that types an Ex command and presses Enter. Two commands chained
-- with no separator means "run them in sequence".
vim.keymap.set('n', '<leader>notes', '<cmd>cd ~/notes/<cr>:e ~/notes<cr>')
vim.keymap.set('n', '<leader>code',  '<cmd>cd ~/code/<cr>:e ~/code<cr>')

-- `<leader>rm` deletes the file backing the current buffer, then closes
-- the buffer. We wrap it in a Lua function so we can GUARD against:
--   1. Non-file buffers (help, terminal, quickfix) — `delete()` would
--      silently fail and `bdelete!` would still close the buffer.
--   2. Buffers whose file isn't readable (deleted on disk, no
--      permission, unsaved scratch buffer).
--   3. Failed deletes — we report the error instead of closing anyway.
vim.keymap.set('n', '<leader>rm', function()
  -- Full path of the file backing the current buffer (or '' if none).
  local path = vim.api.nvim_buf_get_name(0)
  -- vim.bo.buftype is '' for a normal file buffer; for help/terminal/
  -- quickfix/etc. it's a non-empty string like 'help' or 'terminal'.
  if vim.bo.buftype ~= '' or path == '' or vim.fn.filereadable(path) ~= 1 then
    vim.notify('Not a readable file: ' .. path, vim.log.levels.WARN)
    return
  end
  -- vim.fn.delete returns 0 on success, non-zero on failure.
  if vim.fn.delete(path) ~= 0 then
    vim.notify('Failed to delete ' .. path, vim.log.levels.ERROR)
    return
  end
  -- `:bdelete!` closes the buffer. The `bang = true` discards any
  -- unsaved changes — safe here because we just deleted the file.
  vim.cmd.bdelete({ bang = true })
end)

-- `<leader>load` reloads every buffer from disk, discarding unsaved
-- edits. `:bufdo` runs the following command in every buffer; `e!`
-- means "edit with bang" = "reload from disk, throw away changes".
vim.keymap.set('n', '<leader>load', '<cmd>:bufdo e!<cr>')

-- Split navigation using Alt+H/J/K/L (instead of the default Ctrl-W
-- h/j/k/l). The RHS strings are built-in Vim normal-mode commands:
-- <C-w>h means "press Ctrl-W then h" = "go to the window on the left".
vim.keymap.set('n', '<A-h>', '<C-w>h')
vim.keymap.set('n', '<A-j>', '<C-w>j')
vim.keymap.set('n', '<A-k>', '<C-w>k')
vim.keymap.set('n', '<A-l>', '<C-w>l')

-- Split resizing (also Alt-modified).
--   <C-w>+ : taller     <C-w>- : shorter
--   <C-w>< : narrower   <C-w>> : wider
vim.keymap.set('n', '<A-=>', '<C-w>+')
vim.keymap.set('n', '<A-->', '<C-w>-')
vim.keymap.set('n', '<A-.>', '<C-w><')
vim.keymap.set('n', '<A-,>', '<C-w>>')

-- Buffer navigation.
--
-- Note: the <S-h>/<S-l> "go to previous/next buffer" keymaps used to
-- live here, but they're now defined in plugin/bufferline.lua so they
-- can use bufferline's sorted order (not vim's buffer-stack order).
vim.keymap.set('n', '<leader>q', '<cmd>bdelete<cr>')

-- GUI-editor style bindings:
--   Ctrl-N : new buffer (mimics "new tab" in browsers/VSCode)
--   Ctrl-S : save the current file
vim.keymap.set('n', '<C-n>', '<cmd>enew<cr>')
vim.keymap.set('n', '<C-s>', '<cmd>w<cr>')
