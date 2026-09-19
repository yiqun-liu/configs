-- plugin/minuet.lua — AI ghost-text completion (minuet-ai.nvim).
--
-- minuet-ai fetches LLM completions and renders them as virtual text
-- (ghost text) at the cursor. Auto-trigger mode: suggestions appear on
-- typing pauses (minuet debounces and cancels stale requests itself);
-- accept/dismiss/cycle keys are mapped explicitly (see keymap below).
--
-- Deliberately NO nvim-cmp involvement: cmp stays the symbol/snippet
-- menu engine (see plugin/cmp.lua), minuet draws ghost text beside it.
-- Mixing minuet into cmp's sources with a manual-only trigger does not
-- work (cmp never re-filters late async items and resets the source on
-- the next keystroke) — the virtualtext frontend is upstream's
-- recommended path and the only one verified here.
--
-- Provider: DeepSeek FIM (fill-in-the-middle) via its OpenAI-compatible
-- endpoint. FIM sends prefix AND suffix context, so suggestions fit the
-- middle of a file, not just appends. Requires $DEEPSEEK_API_KEY in the
-- environment (minuet reads the env-var NAME below, never the value).

local config = require('tools.config')

vim.pack.add({
  { src = config.github_url('milanglacier/minuet-ai.nvim'), version = 'main' },
})

require('minuet').setup({
  provider = 'openai_fim_compatible',
  provider_options = {
    openai_fim_compatible = {
      end_point = 'https://api.deepseek.com/beta/completions',
      api_key = 'DEEPSEEK_API_KEY',
      model = 'deepseek-flash',
      name = 'Deepseek', -- display name in notifications
    },
  },

  -- Boundary-duplication trim: DeepSeek FIM sometimes restarts the
  -- completion slightly before the cursor, restating text that was just
  -- typed. Both filter lengths default to 0 for FIM providers (on the
  -- assumption the model sees prefix+suffix and behaves); re-enable the
  -- client-side trim of candidate text overlapping pre/post-cursor
  -- context. Only overlaps >= the threshold at the head/tail are cut.
  before_cursor_filter_length = 15,
  after_cursor_filter_length = 15,

  -- Narrow the stale-context window: keystrokes typed while a request is
  -- in flight are invisible to it, and the throttle window (default
  -- 1000ms) suppresses refetch during that time. 600ms trades a few more
  -- parallel FIM calls for fresher context.
  throttle = 600,

  virtualtext = {
    -- Auto-trigger in every filetype. Requests fire on typing pauses;
    -- cost/latency dials if ever needed: narrow this list (e.g.
    -- { 'python', 'lua' }) or cap tokens via provider optional fields.
    auto_trigger_ft = { '*' },

    -- Telescope's prompt buffer has filetype 'TelescopePrompt', so the
    -- '*' wildcard above would enable ghost text (and API calls) inside
    -- every picker's prompt. Excluding it keeps pickers like <C-p>
    -- (find_files) AI-free.
    auto_trigger_ignore_ft = { 'TelescopePrompt' },

    -- Show ghost text while the cmp menu is open (default false hides
    -- it, which would suppress suggestions during most typing since
    -- cmp auto-opens).
    show_on_completion_menu = true,

    -- n_completions defaults to 3, so every trigger already fetches
    -- several alternatives (parallel FIM requests); M-n/M-p cycle through
    -- them and double as manual invoke when nothing is shown yet.
    -- Alt-modifier family avoids cmp's Ctrl keys and the tmux-reserved
    -- Alt keys.
    keymap = {
      accept = '<M-y>',
      accept_line = '<M-a>',
      dismiss = '<M-e>',
      next = '<M-n>',
      prev = '<M-p>',
    },
  },
})
