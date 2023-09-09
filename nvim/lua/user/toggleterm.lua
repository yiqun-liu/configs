-- terminal configurations
-- command examples:
-- 	ToggleTerm size=40 direction=vertical
-- 	TermExec cmd='htop'

local term = require('toggleterm')

term.setup ({
	-- keymap
	open_mapping = [[<c-\>]],

	-- alternatives: horizontal, vertical
	direction = 'float',

	-- appearance for floating terminals
	float_opts = {
		border = 'curved',
		winblend = 30,
	},
})

-- show htop
vim.keymap.set('n', '<leader>htop', '<cmd>TermExec cmd="htop"<cr>')

