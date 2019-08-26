from homely.files import symlink, mkdir
from homely.install import installpkg
from homely.system import execute, haveexecutable
from os import environ
from os.path import exists
from os.path import expanduser
from os.path import isfile
import os
import subprocess

home = expanduser("~")

########## DIRECTORIES ##########
mkdir('~/.config/sublime-text-3/Packages')
mkdir('~/.config/sublime-text-3/Packages/User')

########## PACKAGES #############
installpkg('curl', apt='curl')
installpkg('git', apt='git')
installpkg('wget', apt='wget')
installpkg('zsh', apt='zsh')
installpkg('xdotool', apt='xdotool')

########## SYMLINKS #############
# execute(['rm', home + '/.zshrc'])
symlink('configs/.zshrc', '~/.zshrc')
symlink('configs/.bashrc', '~/.bashrc')
symlink('configs/sublime', '~/.config/sublime-text-3/Packages/User')
symlink('configs/anki', '~/.local/share/Anki2/addons21')


########## COMPOSITE COMMANDS ######################################################


# Install Oh-My-Zsh
if exists(home + '/.oh-my-zsh'):
    print("Oh-My-Zsh is already installed.")
else:
    command = "sh -c \"$(wget -O- https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)\""
    subprocess.call(command, shell=True)

# Change default shell to Oh-My-Zsh
if environ['SHELL'] != '/usr/bin/zsh':
    command = "chsh -s $(which zsh)"
    subprocess.call(command, shell=True)
else:
    print("Zsh is already the default shell.")

# Install Google-Chrome
if haveexecutable('google-chrome'):
    print("Google Chrome is already installed.")
else:
    print("Installing Google Chrome")
    command = """
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    apt update
    apt install google-chrome-stable
    """
    subprocess.call(command, shell=True)

# Install Sublime-Text
if haveexecutable('subl'):
    print("Sublime-Text is already installed.")
else:
    print("Installing Sublime-Text-3")
    command = """
    wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
    sudo apt-get install apt-transport-https
    echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
    apt update
    apt install sublime-text
    """
    subprocess.call(command, shell=True)

# Install Sublime-Text package manager
if exists(home + '/.config/sublime-text-3/Installed Packages/Package Control.sublime-package'):
    print("Sublime-Text-3 Package Manager is already installed.")
else:
    command = "wget -P ~/.config/sublime-text-3/Installed Packages/ https://packagecontrol.io/Package%20Control.sublime-package"
    subprocess.call(command, shell=True)

# Install KeePass2
if haveexecutable('keepass2'):
    print('keepass2 is already installed')
else:
    command = """
    apt-add-repository ppa:jtaylor/keepass
    apt update
    apt install keepass2
    """
    subprocess.call(command, shell=True)