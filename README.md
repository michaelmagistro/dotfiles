# Michael's Dotfiles for Linux OS

## Installation

### Stage 0: The Repository

To get started (fill in)

Before we begin, just some reminders. You need the following:

* Your github login details
* An ssh key generated for Github
* Your password manager handy if you don't know them by heart.

### Stage 1: The Shell

* Install git `sudo apt install git`
* Clone the dotfiles repo
* Run shell.sh
* Run the command `chsh -s $(which zsh)` then **logout** and log back in to access zsh shell.
    * This command needs to run out side of stage1.sh because it needs to be run as the user to affect the user's shell.

### Stage 2: The Apps



### Stage 3: The Environment



### Need to add these commands to the readme:

new linux box

need ~/projects/.dotfiles folder
initialize the bare repo there

git init --bare $HOME/projects/.dotfiles
alias config='/usr/bin/git --git-dir=$HOME/projects/.dotfiles/ --work-tree=$HOME'
config config --local status.showUntrackedFiles no
echo "alias config='/usr/bin/git --git-dir=$HOME/projects/.dotfiles/ --work-tree=$HOME'" >> $HOME/.bashrc


then, after ZSH is installed (after stage 1)


echo "alias config='/usr/bin/git --git-dir=$HOME/projects/.dotfiles/ --work-tree=$HOME'" | sudo tee -a $HOME/.zshrc


config ls-tree --full-tree -r HEAD
