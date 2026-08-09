-- tools/config.lua — a tiny helper module shared by every plugin/*.lua.
--
-- This file is a Lua module. In Neovim, a Lua module is just a file under
-- `lua/` that returns a table. Anyone can grab the same table by calling
-- `require('tools.config')` — Neovim caches it, so the file is loaded
-- only once per session (singleton pattern).
--
-- What this module owns:
--   - `git_scheme`: which transport ('https' or 'ssh') to use for
--     cloning plugins from GitHub. Set once at the top of init.lua,
--     read by every plugin/*.lua via `github_url(repo)`.
--   - `github_url(repo)`: turns an "owner/name" string (like
--     'nvim-treesitter/nvim-treesitter') into a full clone URL.

-- Start with an empty table. We'll attach fields and methods to it,
-- then return it at the bottom.
local M = {}

-- Note: we deliberately do NOT set a default for M.git_scheme here.
-- It is set exclusively by init.lua at startup. If init.lua is somehow
-- bypassed, M.git_scheme stays nil and github_url() returns the https
-- URL (because the `if M.git_scheme == 'ssh'` check fails through to
-- the https branch) — a visible, sensible fallback rather than a
-- silent wrong default.

-- Convert an "owner/name" GitHub repo id into a full git clone URL.
--   repo    : e.g. 'nvim-treesitter/nvim-treesitter'
--   returns : e.g. 'https://github.com/nvim-treesitter/nvim-treesitter.git'
--             or     'git@github.com:nvim-treesitter/nvim-treesitter.git'
-- Both forms are accepted by `git clone`. The `.git` suffix is optional
-- for git itself but is included because that's what `vim.pack` expects
-- in its `src` field.
function M.github_url(repo)
  if M.git_scheme == 'ssh' then
    -- SSH form: git@github.com:OWNER/NAME.git
    -- The colon between host and path (not a slash) is the SSH URL
    -- syntax for "log in as user 'git' and access this path".
    return 'git@github.com:' .. repo .. '.git'
  end
  -- HTTPS form (also the fallback when git_scheme is nil or anything
  -- other than exactly 'ssh').
  return 'https://github.com/' .. repo .. '.git'
end

-- Return the module table. After this line runs, every later
-- `require('tools.config')` call (from anywhere) returns the same M.
return M
