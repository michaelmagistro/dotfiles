#!/bin/zsh
#


# Create necessary directories and variables
dir=~/dotfiles
configdir=~/dotfiles/configs
olddir=~/dotfiles_old
mkdir -p $olddir
cd $configdir

# Config file or folder path list
files=(
  ".bashrc"
  ".zshrc"
)

# Backup any existing configs and create a symlink in their place
for file in ${files[@]}; do
  echo "Move existing files to $olddir"
  mv ~/$file $olddir
  echo "Creating symlink to $file in home directory."
  ln -s $configdir/$file ~/$file
done
