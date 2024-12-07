" highlight syntax
syntax on
" line number (relative)
set relativenumber
" cursor position
set ruler

" highlight the line where cursor is in
set cursorline
" " highlight the line where cursor is in only in insertion mode
" autocmd InsertEnter * set cursorline
" autocmd InsertLeave * set nocursorline

" do not highlight all search result; only highlight them when we are typing
" in the keywords
set nohlsearch
set incsearch

" keep a line margin while browsing
set scrolloff=8

" column marker
set colorcolumn=100

" automatic indentation
set smartindent

" auto complete file names in :e commands
set wildmode=longest,list,full
set wildmenu

" vsplit on the right side
set splitright

" show the command we have typed in
set showcmd

" always show the status bar
set laststatus=2

" set default colorscheme
colorscheme desert

""""""""""""""""""""""""""""""""""""""""
" command remapping
""""""""""""""""""""""""""""""""""""""""
" remap a few common commands to tolerate typos
command W w
command Q q
command WQ wq
command Wq wq

""""""""""""""""""""""""""""""""""""""""
" normal mode remapping (nnoremap)
" NOTE: the 'no' in 'noremap' stands for non-recursive: not to be overridden
" NOTE: use ':map', ':nmap', ':imap' command to check existing mappings
""""""""""""""""""""""""""""""""""""""""

" \e to enter netrw for directory manipulation (current directory)
nnoremap <leader>e <cmd>Ex<cr>
" \config to enter ~/.vimrc
nnoremap <leader>config <cmd>e ~/.vimrc<cr>
" \notes to enter netrw for directory manipulation (notes directory)
nnoremap <leader>notes <cmd>:cd ~/notes<cr>:e ~/notes<cr>
" \notes to enter netrw for directory manipulation (code directory)
nnoremap <leader>code <cmd>:cd ~/code<cr>:e ~/code<cr>

" alt + h / l to switch between vertical splits
nnoremap <A-h> <C-w>h
nnoremap <A-l> <C-w>l
" Some terminal (like konsole) does not treat alt the way we expect. One workaround:
"   https://vi.stackexchange.com/questions/38848/how-can-i-map-ctrl-alt-letter-mappings-in-vim
" One fix to reconfigure the terminal to stick to the traditional way (not possible for konsole)
" The other way to let vim adapt to the terminal
"   https://vi.stackexchange.com/questions/2350/how-to-map-alt-key
" But this makes the processing of Esc key problematic... I would use the legacy C-w instead
" execute "set <M-h>=\eh"
" nnoremap <M-h> <C-w>h
" execute "set <M-l>=\el"
" nnoremap <M-l> <C-w>l

""""""""""""""""""""""""""""""""""""""""
" insert mode remapping (inoremap)
""""""""""""""""""""""""""""""""""""""""

" (no remap yet)
