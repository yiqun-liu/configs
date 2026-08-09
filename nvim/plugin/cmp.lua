-- plugin/cmp.lua — autocompletion menu.
--
-- nvim-cmp is the completion engine: as you type in insert mode, it
-- pops up a menu of candidate completions drawn from various SOURCES.
-- We install cmp itself plus five sources (each source is a small
-- plugin that knows how to fetch completions of one kind):
--
--   cmp-nvim-lsp  : completions from the attached LSP server (functions,
--                   types, variables in your codebase)
--   cmp-buffer    : completions from words already in the current buffer
--   cmp-path      : filesystem path completions (e.g. /usr/bin/...)
--   cmp-cmdline   : completions when typing `:` / `/` / `?` commands
--   cmp_luasnip   : snippet-aware completions (snippet triggers show up
--                   in the menu; selecting one expands the snippet)
--
-- PRECONDITION (for snippet expansion only): plugin/luasnip.lua must
-- run `vim.pack.add(LuaSnip)` before any snippet is expanded at user
-- time. This is satisfied automatically by Neovim's alphabetical
-- plugin/ sourcing: luasnip.lua runs AFTER cmp.lua alphabetically, but
-- cmp.lua only calls `require('luasnip')` inside the `snippet.expand`
-- closure (line ~24 below), which fires at user time (when a snippet
-- is actually being expanded), NOT at module load time. So the load
-- order is fine; the dependency just isn't visible from cmp.lua's
-- imports. If you ever reorganize plugin/luasnip.lua, keep this in
-- mind.

local config = require('tools.config')

vim.pack.add({
  { src = config.github_url('hrsh7th/nvim-cmp'),      version = 'main' },
  { src = config.github_url('hrsh7th/cmp-nvim-lsp'),  version = 'main' },
  { src = config.github_url('hrsh7th/cmp-buffer'),    version = 'main' },
  { src = config.github_url('hrsh7th/cmp-path'),      version = 'main' },
  { src = config.github_url('hrsh7th/cmp-cmdline'),   version = 'main' },
  -- cmp_luasnip's default branch is 'master' (not 'main') — verified
  -- against the GitHub repo. Don't "fix" this to 'main'.
  { src = config.github_url('saadparwaiz1/cmp_luasnip'), version = 'master' },
})

local cmp = require('cmp')

-- Main setup: configure how cmp behaves in INSERT mode.
cmp.setup({
  -- `snippet.expand` is called by cmp when an LSP server returns a
  -- snippet (e.g. "fn($1) {$2}" with placeholders). We hand the
  -- snippet body to LuaSnip, which knows how to render the
  -- placeholders as jumpable cursor positions.
  snippet = {
    expand = function(args)
      require('luasnip').lsp_expand(args.body)
    end,
  },

  -- Key mappings for the completion menu. `cmp.mapping.preset.insert`
  -- returns a set of defaults (C-n/C-p/C-y/C-e — see below); we override
  -- and add the keys we care about.
  --
  -- Context: these mappings work ONLY in INSERT mode (and SELECT mode
  -- for Tab/S-Tab). They do NOT work in cmdline or normal mode. Cmdline
  -- has its own separate preset (see cmp.setup.cmdline below).
  mapping = cmp.mapping.preset.insert({
    -- <C-l> manually triggers the completion menu. Replaces the
    -- conventional <C-Space> (which conflicts with IME toggle for
    -- CJK input methods). Works only in INSERT mode.
    ['<C-l>'] = cmp.mapping.complete(),

    -- <CR> (Enter) confirms the highlighted item. select = true means
    -- "if nothing is highlighted, pick the first item." Convenient but
    -- can cause accidental confirms; set to false if that bothers you.
    ['<CR>'] = cmp.mapping.confirm({ select = true }),

    -- Tab / Shift-Tab are LuaSnip-AWARE: if the cursor is inside an
    -- active snippet, Tab jumps to the next placeholder instead of
    -- just selecting the next completion item. Without this, snippets
    -- would expand but be unnavigable.
    --
    -- The closures take a `fallback` arg: if none of the snippet/cmp
    -- branches apply, we call `fallback()` to defer to the default
    -- Tab behavior (indenting, etc.). The `modes = { 'i', 's' }`
    -- arg makes the mapping apply in both INSERT and SELECT modes
    -- (SELECT mode is the transient mode you're in right after
    -- picking a completion item).
    ['<Tab>'] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_next_item()                              -- menu open → next item
      elseif require('luasnip').expand_or_jumpable() then
        require('luasnip').expand_or_jump()                 -- snippet → expand or jump
      else
        fallback()                                          -- otherwise default Tab
      end
    end, { 'i', 's' }),
    ['<S-Tab>'] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_prev_item()                              -- menu open → prev item
      elseif require('luasnip').jumpable(-1) then
        require('luasnip').jump(-1)                         -- snippet → jump backward
      else
        fallback()                                          -- otherwise default S-Tab
      end
    end, { 'i', 's' }),
  }),

  -- Sources cmp draws from, in priority order. `cmp.config.sources`
  -- takes groups; within a group, all sources contribute; later
  -- groups are de-prioritized (their items appear lower in the menu).
  sources = cmp.config.sources(
    { { name = 'nvim_lsp' }, { name = 'luasnip' } },  -- high priority
    { { name = 'buffer' } }                           -- lower priority
  ),
})

-- Filetype-specific configuration: in gitcommit buffers (the editor
-- that opens when you type `git commit` without `-m`), snippets and
-- LSP completions aren't useful (you're typing a free-form message).
-- Restrict to buffer-word completion only.
--
-- Note: this only works if $EDITOR (or $GIT_EDITOR) is set to nvim,
-- so that git launches Neovim for the commit message. If $EDITOR is
-- set to another editor (vim, nano, code, etc.), this config never
-- activates because Neovim isn't the one opening COMMIT_EDITMSG.
-- To test manually: open any buffer and run :set filetype=gitcommit.
cmp.setup.filetype('gitcommit', {
  sources = cmp.config.sources({ { name = 'buffer' } }),
})

-- Cmdline configuration for `/` and `?` (search). Only buffer-word
-- completion makes sense here (you're searching for words in the file).
cmp.setup.cmdline({ '/', '?' }, {
  mapping = cmp.mapping.preset.cmdline(),
  sources = { { name = 'buffer' } },
})

-- Cmdline configuration for `:` (Ex commands). Path completion first
-- (for `:e /usr/bin/...`), then cmdline completion (for `:bufdo`,
-- `:LspInfo`, etc.). The order matters: path first means typing a
-- path prefix shows file candidates before command-name candidates.
cmp.setup.cmdline(':', {
  mapping = cmp.mapping.preset.cmdline(),
  sources = cmp.config.sources({ { name = 'path' } }, { { name = 'cmdline' } }),
})
