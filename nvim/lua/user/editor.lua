-- General settings for the editor

-- diable mouse
vim.opt.mouse = ""

-- show absolute line number of current and relative line numbers for other lines
vim.opt.number = true
vim.opt.relativenumber = true

-- highlight current line
vim.opt.cursorline = true

-- indentation
vim.opt.smartindent = true

-- highlighting: highlight when typing search keywords, disable highlighting when keywords entered
vim.opt.hlsearch = false
vim.opt.incsearch = true

-- browsing margin
vim.opt.scrolloff = 8

-- markers
vim.opt.colorcolumn = '100'

-- pane split: when running ':vsplit', put the new split on the right
vim.opt.splitright = true

-- use true colors - so that we could have have visual effects such as "transparency"
vim.opt.termguicolors = true
