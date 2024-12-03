# Configurations

A repo of Yiqun's personal configuration files. The goal is to make my configurable software behaves
consistently on all machines. The `manage.sh` script could gather (for persisting) and distribute
(for deployment) the configuration files from / to their working path.

The configs mostly come from the official guide and demand-driven searching. Some ideas are taken
from projects like [lazyVim](https://www.lazyvim.org/).

## Usage

```bash
# create a working copy
cp tracked-configs.example tracked-configs

# custmoize the file when necessary
nvim tracked-configs

# to persist local changes
./manage.sh collect
# git push origin main

# to put the configs into effect
# git pull origin main
./manage.sh deploy
```

Remember that the configurations could have external dependencies. Take `nvim` as an example, we
have to manually install the package manager (then download all packages) and the LSP servers.

Sometimes there are compiled files or downloaded files which we would not like to persist in this
repo. We filter them out with the top level `.gitignore`.

## TODO

- Support single file config like `.gitconfig`, `.vimrc`.
- Include a `.vimrc` file as a reasonble fallback.
- nvim: consider how to manage project-local settings (indentations).
- manage.sh diff

