from homely.files import symlink


symlink('configs/.zshrc', '~/.zshrc')
symlink('configs/.bashrc', '~/.bashrc')
symlink('configs/sublime', '~/.config/sublime-text-3/Packages/User')
symlink('configs/anki', '~/.local/share/Anki2/addons21')