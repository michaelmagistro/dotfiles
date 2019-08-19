#!/bin/bash
#
# Repo: michaelmagistro/dotfiles
# Stage 1 Installation: The Shell -- ZSH
# S


set -e
sudo -v

alias cp='cd ~/projects'

# zsh prereqs

if [ ! -d curl ]; then
echo 'Installing curl...'
apt install curl
fi

if [ ! -d git ]; then
echo 'Installing git...'
apt install git
fi

# install zsh

if [ ! -d zsh ]; then
echo 'Installing zsh...'
apt install zsh
fi

set +e

echo 'Installing oh-my-zsh...'
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

echo "Now, run the command 'chsh -s \$(which zsh)' and then logout & log back in and start the shell"

