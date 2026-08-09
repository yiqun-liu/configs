-- plugin/telescope.lua — fuzzy finder over files, buffers, grep, etc.
--
-- Telescope is a highly extensible fuzzy finder. We install it and its
-- hard dependency plenary.nvim in one `vim.pack.add` call (grouping
-- them together avoids the cross-file load-order problem).
--
-- After install, we wire up a set of keymaps that invoke telescope's
-- "builtin" finders (find_files, live_grep, etc.).

local config = require('tools.config')

-- Plenary is a utility library telescope depends on; telescope.nvim is
-- the finder itself. Both are on the 'master' branch.
vim.pack.add({
  { src = config.github_url('nvim-lua/plenary.nvim'),   version = 'master' },
  { src = config.github_url('nvim-telescope/telescope.nvim'), version = 'master' },
})

-- `telescope.builtin` is a module containing all the ready-to-use
-- finder functions. We `require` it once here (eager load) so the first
-- keymap press doesn't pay the require cost.
--
-- Note: plenary and telescope must already be on rtp (which they are,
-- because `vim.pack.add` above added them synchronously) for this
-- require to succeed.
local builtin = require('telescope.builtin')
local actions = require('telescope.actions')

-- ============================================================================
-- Keymaps: conventional <leader>f* prefix (mnemonic: "find").
-- Each maps to one builtin finder; pressing it opens telescope's
-- floating-window picker for that search type.
-- ============================================================================

vim.keymap.set('n', '<leader>ff', builtin.find_files, {})  -- find files by name
vim.keymap.set('n', '<leader>fg', builtin.live_grep, {})  -- live grep (ripgrep)
vim.keymap.set('n', '<leader>fb', builtin.buffers, {})    -- find open buffers
vim.keymap.set('n', '<leader>fh', builtin.help_tags, {})  -- search :help tags

-- ============================================================================
-- Keymaps: muscle-memory aliases (single chord, no <leader> prefix).
-- These mirror what many users are used to from other editors.
-- ============================================================================

-- <C-p> (Ctrl-P) is a conventional "find file" binding in many editors.
-- Note: <C-p> in vim's normal mode is also a synonym for `k` (move up
-- one line), but that's redundant — `k` already exists — so it's safe
-- to repurpose.
vim.keymap.set('n', '<C-p>', builtin.find_files, {})

-- <C-g> shows the file's name and path in vim by default; we override
-- it with "find git-tracked files" (skips ignored files like build
-- artifacts). Useful in repos with many untracked files.
vim.keymap.set('n', '<C-g>', builtin.git_files, {})

-- <leader>grep is a longer alias for live_grep — convenient when you
-- want the search to be obvious in `:map` output and don't mind the
-- extra keystrokes.
vim.keymap.set('n', '<leader>grep', builtin.live_grep, {})

-- ============================================================================
-- Keymaps: screen-aware LSP jump (opens in a NEW split, direction chosen
-- by the current window's aspect ratio).
--
-- Convention: `<leader>{keys}` = smart-split version of the in-place
-- `{keys}` action. So `<leader>gd` parallels our `gd` (in-place jump to
-- definition), and `<leader>grr` parallels the Neovim 0.11+ default
-- `grr` (in-place references list). Both use smart_lsp_jump to open the
-- result in a vsplit (if the window is wide) or split (if it's tall).
-- ============================================================================

-- smart_lsp_jump chooses vsplit or split based on the current window's
-- width vs height. If the window is wider than tall (landscape), vsplit
-- gives two side-by-side panes. If taller than wide (portrait), split
-- gives two stacked panes with full width preserved.
--
-- Note: terminal characters are ~2:1 (width:height), so a window that's
-- 80 cols × 40 rows looks roughly square on screen. With the simple
-- winwidth >= winheight comparison, such a window gets vsplit. If you
-- find that too aggressive, change to winwidth >= winheight * 2.
--
-- Both single-result and multi-result cases are handled:
--   - Single result: jump_type controls where the result opens
--   - Multiple results: attach_mappings overrides Enter to use the
--     same split direction as jump_type
local function smart_lsp_jump(fn)
  local is_wide = vim.fn.winwidth(0) >= vim.fn.winheight(0)
  local jt = is_wide and 'vsplit' or 'split'
  fn({
    jump_type = jt,
    attach_mappings = function(_, _)
      actions.select_default:replace(
        is_wide and actions.select_vertical or actions.select_horizontal
      )
      return true
    end,
  })
end

vim.keymap.set('n', '<leader>gd', function() smart_lsp_jump(builtin.lsp_definitions) end)
vim.keymap.set('n', '<leader>grr', function() smart_lsp_jump(builtin.lsp_references) end)
