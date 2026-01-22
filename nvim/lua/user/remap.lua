-- Memo:
-- vim.keymap.set( mode, key(s), vim_operations or original vim-keys )

-- directory manipulation with netrw
vim.keymap.set('n', '<leader>e', vim.cmd.Ex)
vim.keymap.set('n', '<leader>config', '<cmd>:cd ~/.config/nvim/<cr>:e ~/.config/nvim/<cr>')
vim.keymap.set('n', '<leader>notes', '<cmd>:cd ~/notes/<cr>:e ~/notes<cr>')
vim.keymap.set('n', '<leader>code', '<cmd>:cd ~/code/<cr>:e ~/code<cr>')
-- delete current file and close buffer
vim.keymap.set('n', '<leader>rm', '<cmd>:call delete(expand(\'%:p\')) | bdelete!<cr>')
-- reload all buffers from disk
vim.keymap.set('n', '<leader>load', '<cmd>:bufdo e!<cr>')

-- switch between splits
vim.keymap.set('n', '<A-h>', '<C-w>h')
vim.keymap.set('n', '<A-j>', '<C-w>j')
vim.keymap.set('n', '<A-l>', '<C-w>l')
vim.keymap.set('n', '<A-k>', '<C-w>k')

-- move split boundaries
vim.keymap.set('n', '<A-=>', '<C-w>+')
vim.keymap.set('n', '<A-->', '<C-w>-')
vim.keymap.set('n', '<A-.>', '<C-w><')
vim.keymap.set('n', '<A-,>', '<C-w>>')

-- buffer manipulations
vim.keymap.set('n', '<S-h>', '<cmd>bprev<cr>')
vim.keymap.set('n', '<S-l>', '<cmd>bnext<cr>')
vim.keymap.set('n', '<leader>q', '<cmd>bdelete<cr>')

-- some useful keys from GUI-based editors
-- new file: ctrl + n
vim.keymap.set('n', '<C-n>', '<cmd>enew<cr>')
-- save file: ctrl + s
vim.keymap.set('n', '<C-s>', '<cmd>w<cr>')

