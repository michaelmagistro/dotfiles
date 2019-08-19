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
  ".config/sublime-text-3/Packages/User"
  ".local/share/Anki2/addons21"
)

function isdir () {
    echo "entering isdir function"
    echo "Variable in question: $1"
    if [[ -d $1 ]]; then
        echo 'this is a directory'
    elif [[ -f $1 ]]; then
        echo 'this is -f'
    else
        echo 'this is neither a directory or file'
    fi
}

for file in ${files[@]}; do
    isdir ~/$file
done

echo "stage1 complete"

for file in ${files[@]}; do
    isdir $configdir/$file
done

# # Backup any existing configs and create a symlink in their place
# for file in ${files[@]}; do
#   echo "Move existing files to $olddir"
#   mv ~/$file $olddir
#   echo "creating symlinks.."
#   if [ -d ~/$file ]
#   then
#     if [ ! -d $configdir/$file ]
#     then
#       mkdir -p $configdir/$file
#     fi
#     ln -s $configdir/$file ~/$file
#   else
#     ln -s $configdir/$file ~/$file
#   fi
# done
