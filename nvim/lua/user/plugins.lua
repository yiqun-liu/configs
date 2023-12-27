vim.cmd [[packadd packer.nvim]]

packer = require('packer')

-- Ask packet to access git via ssh could improve access stability in mainland China. Don't know
-- why, just know it works.
packer.init({
	git = {
		default_url_format = 'git@github.com:%s'
	}
})

packer.startup(function(use)

	-- package manager itself
	use 'wbthomason/packer.nvim'

	-- fuzzy file finder
	use {
		'nvim-telescope/telescope.nvim', tag = '0.1.2',
		requires = 'nvim-lua/plenary.nvim'
	}

	-- terminal
	use 'akinsho/toggleterm.nvim'

	-- buffer line
	use {'akinsho/bufferline.nvim', requires = 'nvim-tree/nvim-web-devicons'}

	-- nvim-tree sitter
	use {'nvim-treesitter/nvim-treesitter', run = ':TSUpdate'}

	-- LSP-related
	-- LSP server configurations
	use 'neovim/nvim-lspconfig'
	-- auto-completion: framework
	use 'hrsh7th/nvim-cmp'
	-- auto-completion: snippets source
	use 'hrsh7th/cmp-nvim-lsp'
	use 'hrsh7th/cmp-buffer'
	use 'hrsh7th/cmp-path'
	use 'hrsh7th/cmp-cmdline'
	-- auto-completion: recommendation maker & its adaptor
	use {'L3MON4D3/LuaSnip', run = 'make install_jsregexp'}
	use 'saadparwaiz1/cmp_luasnip'

	-- colorscheme
	use {'catppuccin/nvim', as = 'catppuccin'}
end)
