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
        echo "This is a directory: return code 2"
        return 2
    elif [[ -f $1 ]]; then
        echo "This is a file: return code 1"
        return 1
    else
        echo "This is neither a directory nor file: return code 3"
        return 3
    fi
}

for file in ${files[@]}; do
    isdir ~/$file ; echo $?
done

echo "stage1 complete"

for file in ${files[@]}; do
    isdir $configdir/$file ; echo $?
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
