# Get the current OS
os=$(uname)
echo "Version 1.0"

# export (set) variables
export PROJECTS_HOME=~/p38 # project home path
export PRT_SPEC=~/prt_spec # portable software folder with specific configurations to this device
export PRT_GEN=~/prt_gen # portable software folder with general configurations
export PRT_DROP=~/Dropbox/prt # portable software folder in dropbox
export PVENV=~/pvenv # python virtual environments folder

# Copy the current directory path to the Clipboard
	alias cpwd="pwd | tr -d '\n' | pbcopy && echo 'pwd copied to clipboard'"

# Grep Aliases
    alias gp="grep --color=auto"
    alias gpi="grep -i --color=auto"
    alias gpr="grep -r --color=auto"
    alias gprn="grep -rn --color=auto"
    alias gprni="grep -rni --color=auto"
    alias gprv="grep -rv --color=auto"
    alias gprnv="grep -rnv --color=auto"
    alias gprnvi="grep -rnvi --color=auto"
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
	alias de="deactivate && unalias py && unalias pys" # deactivate python environment
# flask aliases
    alias fd="flask --app app.py --debug run" # fire up the flask debug server for app.py
# xclip aliases
    alias xclip="xclip -selection clipboard" # copy to clipboard
    alias xclipin="xclip -selection clipboard -in" # copy to clipboard
    alias xclipout="xclip -selection clipboard -out" # paste from clipboard
# path aliases
    alias path="echo -e \$PATH | tr : '\n'" # display all path vars on separate lines

# OS-Specific configurations
if [ "$os" = "Linux" ]; then
    # Perform Linux-specific actions
    echo "OS: Linux"
    # set python venv activation aliases
    na() {
        source "$PWD/.pvenv/bin/activate"
        alias py="$PWD/.pvenv/bin/python"
        alias pys="scrapy runspider"
    }
    # alias code=~/prt_spec/VSCode/Code.exe # git bash exe location

    # Check if running on Windows Subsystem for Linux
    if uname -a | grep -qi "microsoft"; then
        echo "Running on Windows Subsystem for Linux."
    else
        echo "Not running on Windows Subsystem for Linux."
    fi

elif [ "$os" = "Darwin" ]; then    
    # Perform macOS-specific actions
    echo "OS: macOS"
    
elif [[ "$os" == "MINGW64_NT-10.0"* ]] || [[ "$os" == "MSYS_NT-10.0"* ]]; then    
    # Perform Windows-specific actions
    echo "OS: Windows"

    # set portable python variables
    export PY=~/py # python installation folder
    export PATH="$PY:$PATH"
    export PATH="$PY/Scripts:$PATH"

    # set portable software variables for executables
    export BASHBASH=~/prt_gen/GitBash/bin/bash.exe # git bash exe location
    export GITGIT=~/prt_gen/GitBash/bin/git.exe # git.exe location
    # export executables to path
    export PATH="$BASHBASH:$PATH"
    export PATH="$GITGIT:$PATH"

    # set python venv activation aliases
    na() {
        source "$PWD/.pvenv/Scripts/activate"
        alias py="$PWD/.pvenv/Scripts/python.exe"
        alias pys="scrapy runspider"
    }
	
    # set sublime location in dropbox. if that doesn't exist, use prt_spec
	s() {
    if ! $PRT_DROP/SublimeText/sublime_text.exe "$@"; then
        $PRT_SPEC/sublime_text.exe "$@"
    fi
    }

else
    # Perform default actions
    echo "OS: Unknown"
fi

# Device-specific configurations
if [[ -f ~/prt_spec/laptop_lenovo.txt ]]; then
    echo "Device: Lenovo Laptop"
elif [[ -f ~/prt_spec/laptop_lenovo_mint_vm.txt ]]; then
    echo "Device: Lenovo Laptop Mint VM"
elif [[ -f ~/prt_spec/desktop_asc.txt ]]; then
    echo "Device: Desktop Asc"
elif [[ -f ~/prt_spec/desktop_asc_mint_vm.txt ]]; then
    echo "Device: Desktop Asc Mint VM"
elif [[ -f ~/prt_spec/laptop_work.txt ]]; then
    echo "Device: Laptop Work"
elif [[ -f ~/prt_spec/laptop_lenovo_ubuntu_vm.txt ]]; then
    echo "Device: Lenovo Laptop Ubuntu VM"
else
    # Default configurations
    echo "Device: Unknown. Check ~/prt_spec/ for a file with the name of this"
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


# check contents & presence of notable directories
alias prt="echo '
		-= Projects =-'
if [ -d \$PROJECTS_HOME/ ]; then 
    echo '\$PROJECTS_HOME/'
    lsp \$PROJECTS_HOME/ 2>/dev/null || true
    echo ''
    echo 'Nested structure:'
    # Find all level-2 folders, group by parent, print nested bullets
    find \$PROJECTS_HOME/ -mindepth 2 -maxdepth 2 -type d 2>/dev/null | sort | awk -F'/' '
    {
        parent = \$(NF-1)
        child = \$NF
        if (parent != last_parent) {
            if (NR > 1) print \"\"  # blank line between categories only if needed
            print \"* \" parent
            last_parent = parent
        }
        print \"    * \" child
    }'
    echo ''
fi
echo '
		-= Prts =-'
if [ -d \$PRT_DROP/ ]; then echo '\$PRT_DROP/'; lsp \$PRT_DROP/; fi
if [ -d \$PRT_GEN/ ]; then echo '
\$PRT_GEN/'; lsp \$PRT_GEN/; fi
if [ -d \$PRT_SPEC ]; then echo '
\$PRT_SPEC'; lsp \$PRT_SPEC; fi
echo '
		-= Environments =-'
if [ -d \$PY/ ]; then echo '\$PY/'; lsp \$PY; fi
if [ -d \$PVENV ]; then echo '
\$PVENV/'; lsp \$PVENV; fi;"


# check for present of folders
if [ -d "$PROJECTS_HOME" ]; then echo "$PROJECTS_HOME"; else echo "$PROJECTS_HOME is missing"; fi
if [ -d $PRT_DROP ]; then echo "$PRT_DROP"; else echo "$PRT_DROP is missing"; fi
if [ -d $PRT_SPEC ]; then echo "$PRT_SPEC"; else echo "$PRT_SPEC is missing"; fi
if [ -d $PRT_GEN ]; then echo "$PRT_GEN"; else echo "$PRT_GEN is missing"; fi
echo "Projects: " $(ls $PROJECTS_HOME)

# gss() - Git Status Summary for repos in priv, pub, fork, zArch_priv, zArch_pub, zArch_fork
gss() {
    local bases=(priv pub fork zArch_priv zArch_pub zArch_fork)
    for base in "${bases[@]}"; do
        for repo in "$PROJECTS_HOME/$base"/*/; do
            if [ -d "$repo/.git" ]; then
                local status=$(cd "$repo" && gs 2>/dev/null)
                local folder="$base/$(basename "$repo")"
                if echo "$status" | grep -qE "up to date with 'origin/(main|master)'"; then
                    echo "$folder: OK"
                else
                    echo "$folder: Requires Attention"
                fi
            fi
        done
    done
}
