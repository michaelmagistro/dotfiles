# Get the current OS
os=$(uname)

# export (set) variables
export PROJECTS_HOME=~/p38 # project home path
export PRT_SPEC=~/prt_spec # portable software folder with specific configurations to this device
export PRT_GEN=~/prt_gen # portable software folder with general configurations
export PRT_DROP=~/Dropbox/prt # portable software folder in dropbox
export PY=~/py # python installation folder
export PVENV=~/pvenv # python virtual environments folder
export BASHBASH=~/prt_gen/GitBash/bin/bash.exe # git bash exe location
export GITGIT=~/prt_gen/GitBash/bin/git.exe # git.exe location
# export to path
export PATH="$PY:$PATH"
export PATH="$PY/Scripts:$PATH"
export PATH="$BASHBASH:$PATH"
export PATH="$GITGIT:$PATH"

# Copy the current directory path to the Clipboard
	alias cpwd="pwd | tr -d '\n' | pbcopy && echo 'pwd copied to clipboard'"

# Git aliases
	alias gs="git status"
	alias gpom="git push origin main"
	alias gpum="git pull origin main"
	alias gcm="git commit -m"
	alias ga="git add ."
	alias gaa="git add -A"
	alias gd="git diff"
	alias gck="git checkout"
	alias glo="git log --oneline"
	alias gr="git reset"
	alias gb="git branch"
# python aliases
	alias jn="jupyter-notebook"
	alias jl="jupyter-lab"
	alias de="deactivate && unalias py" # deactivate python environment

# Device-specific configurations
if [[ -f ~/prt_spec/laptop_lenovo.txt ]]; then
    echo "Running on Lenovo Laptop"

elif [[ -f ~/prt_spec/laptop_lenovo_mint_vm.txt ]]; then
    echo "Running on Lenovo Laptop Mint VM"

elif [[ -f ~/prt_spec/desktop_asc.txt ]]; then
    echo "Running on Desktop Asc"

elif [[ -f ~/prt_spec/desktop_asc_mint_vm.txt ]]; then
    echo "Running on Desktop Asc Mint VM"

elif [[ -f ~/prt_spec/laptop_work.txt ]]; then
    echo "Running on Laptop Work"

else
    # Default configurations
    echo "Running on an unknown machine"
fi

# Perform different actions based on the OS
if [ "$os" = "Linux" ]; then
    # Perform Linux-specific actions
    echo "Running on Linux"
    #!/bin/bash
    # echo "Do you have sudo access? (y/n)"
    # read -r response
    # if [[ $response == [yY] ]]; then
    #     echo "You have sudo access."
    # else
    #     echo "You do not have sudo access."
    #     export PATH="$HOME/py/bin:$PATH" # export the python bin folder to path to make python and pip commands available
    # fi
elif [ "$os" = "Darwin" ]; then    
    # Perform macOS-specific actions
    echo "Running on macOS"
    
elif [[ "$os" == "MINGW64_NT-10.0"* ]] || [[ "$os" == "MSYS_NT-10.0"* ]]; then    
    # Perform Windows-specific actions
    echo "Running on Windows"
	# alias py="$PY/python.exe"
	# alias pip="$PY/Scripts/pip3.11.exe"
	# alias py64="$PY/py311x64/python.exe"
	# Set Python paths etc..

    # set alias to activate python env & set py alias
    a() {
        local current_folder=$(basename "$PWD")
        source "$PVENV/$current_folder/Scripts/activate"
        alias py="$PVENV/$current_folder/Scripts/python.exe"
        alias pys="scrapy runspider"
    }
	
    # set sublime location in dropbox. if that doesn't exist, use
	s() {
    if ! $PRT_DROP/SublimeText/sublime_text.exe "$@"; then
        $PRT_SPEC/sublime_text.exe "$@"
    fi
    }

else
    # Perform default actions
    echo "Running on an unknown OS"
fi

# folder shortcuts
	alias cdp="cd $PROJECTS_HOME && ls --color -h --group-directories-first" # cd to projects folder

# bash
	alias src="source $PROJECTS_HOME/dotfiles/config/.bashrc" # reload the bashrc file
	alias sb="s $PROJECTS_HOME/dotfiles/config/.bashrc" # open .bashrc in sublime text

# linux folder commands
	alias lsp="ls --color -h --group-directories-first"

# navigation
	alias cdd="cd ~/Dropbox"
	alias cdo="cd ~/Onedrive"
	alias cdg="cd ~/My Drive"
	# e.g. cdl ~/Dropbox
		c() {
		    cd $1 && ls --color -h --group-directories-first
		}

# example portable apps in prt_spec - greenshot, everything search
# example portable apps in prt_gen - gitbash, xlwings

alias prt="
	echo '
		-= Projects =-';
	if [ -d $PROJECTS_HOME/ ]; then
		echo '$PROJECTS_HOME/';
		lsp $PROJECTS_HOME/;
	fi;
	echo '
		-= Prts =-';
	if [ -d $PRT_DROP/ ]; then
		echo '$PRT_DROP/';
		lsp $PRT_DROP/;
	fi;
	if [ -d $PRT_GEN/ ]; then
		echo '
$PRT_GEN/';
		lsp $PRT_GEN/;
	fi;
	if [ -d $PRT_SPEC ]; then
		echo '
$PRT_SPEC
		lsp $PRT_SPEC
	fi;
	echo '
		-= Environments =-';
	if [ -d $PY/ ]; then
		echo '$PY/';
		lsp $PY
	fi;
	if [ -d $PVENV ]; then
		echo '
$PVENV/';
		lsp $PVENV
	fi;"