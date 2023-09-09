-- Memo:
-- vim.keymap.set( mode, key(s), vim_operations or original vim-keys )

-- directory manipulation with netrw
vim.keymap.set('n', '<leader>e', vim.cmd.Ex)

-- switching from vertical splits
vim.keymap.set('n', '<A-h>', '<C-w>h')
vim.keymap.set('n', '<A-l>', '<C-w>l')

-- buffer manipulations
vim.keymap.set('n', '<S-h>', '<cmd>bprev<cr>')
vim.keymap.set('n', '<S-l>', '<cmd>bnext<cr>')
vim.keymap.set('n', '<leader>q', '<cmd>bdelete<cr>')

-- some useful keys from GUI-based editors
-- new file: ctrl + n
vim.keymap.set('n', '<C-n>', '<cmd>enew<cr>')
-- save file: ctrl + s
vim.keymap.set('n', '<C-s>', '<cmd>w<cr>')

