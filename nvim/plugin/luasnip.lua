-- plugin/luasnip.lua — snippet engine.
--
-- LuaSnip is the snippet engine we use for LSP snippet expansion (e.g.
-- auto-complete a function template with placeholders for arguments).
-- It has an optional C extension called "jsregexp" that speeds up
-- regex-based snippet transforms; we build it automatically after
-- install/update via a PackChanged autocmd (see below).
--
-- PRECONDITION FOR cmp.lua: this file must run `vim.pack.add(LuaSnip)`
-- before any snippet expansion happens at user time. Neovim's
-- alphabetical plugin/ sourcing satisfies this — luasnip.lua runs
-- AFTER cmp.lua alphabetically, but cmp.lua only calls
-- `require('luasnip')` inside a closure (at snippet-expansion time,
-- not at load time), so the order is fine. See plugin/cmp.lua for the
-- consumer side of this contract.

local config = require('tools.config')

-- Register an autocmd that fires whenever `vim.pack.add` finishes
-- installing or updating a plugin. The `PackChanged` event is a
-- Neovim 0.12 builtin; its callback receives a table `ev` with:
--   ev.data.spec   — the plugin spec that was just installed/updated
--   ev.data.kind   — 'install', 'update', or 'delete'
--   ev.data.path   — the on-disk path of the plugin
--
-- IMPORTANT: we register this autocmd BEFORE the `vim.pack.add` call
-- below. Why? Because `vim.pack.add` fires `PackChanged` synchronously
-- for any plugin it installs RIGHT NOW (on first run). If we registered
-- the autocmd AFTER `vim.pack.add`, the first-install event would be
-- missed and jsregexp wouldn't be built until the next update.
vim.api.nvim_create_autocmd('PackChanged', {
  desc = 'Build LuaSnip jsregexp after install/update',
  callback = function(ev)
    -- Filter to only LuaSnip install/update events (other plugins'
    -- PackChanged events are irrelevant to us).
    local name = ev.data.spec.name
    local kind = ev.data.kind
    if name ~= 'LuaSnip' then return end
    if kind ~= 'install' and kind ~= 'update' then return end

    -- Run `make install_jsregexp` in the plugin's directory. This
    -- compiles the C extension that LuaSnip uses for regex transforms.
    --
    -- `vim.system` runs the command ASYNCHRONOUSLY (so the editor
    -- doesn't freeze during the build). The third arg is an `on_exit`
    -- callback that runs when the command finishes — on a background
    -- thread, so we wrap our `vim.notify` in `vim.schedule` to push
    -- the notification back onto Neovim's main event loop (API calls
    -- like vim.notify are not safe to call from off-main threads).
    vim.system({ 'make', 'install_jsregexp' }, { cwd = ev.data.path }, function(result)
      vim.schedule(function()
        -- result.code is the process exit code (0 = success).
        if result.code == 0 then
          vim.notify('[luasnip] jsregexp built (' .. ev.data.path .. ')', vim.log.levels.INFO)
        else
          -- result.stderr may be nil if make produced no stderr;
          -- `or ''` falls back to an empty string so the `..` concat
          -- doesn't throw on nil.
          vim.notify('[luasnip] jsregexp build failed: ' .. (result.stderr or ''), vim.log.levels.ERROR)
        end
      end)
    end)
  end,
})

-- Now actually install LuaSnip. If it's already installed (and the
-- lockfile matches), this is a no-op except for adding the path to rtp.
vim.pack.add({
  { src = config.github_url('L3MON4D3/LuaSnip'), version = 'master' },
})
