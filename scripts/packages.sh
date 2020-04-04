#!/bin/zsh
#
# Install Apps and Packages
# This file is part of michaelmagistro/dotfiles
# Any additional programs can be added in any order


# Install XDOTool
xdotool --version
if [ $? != 0 ]
then
  apt install xdotool
else
  echo 'xdotool is already installed'
fi


# Install Google Chrome
google-chrome --version
if [ $? != 0 ]
then
  echo 'Installing Google Chrome... see https://www.ubuntuupdates.org/ppa/google_chrome'
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
  sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
  apt update
  apt install google-chrome-stable
else
  echo 'Google Chrome is already installed.'
fi


# Install Sublime Text
subl --version
if [ $? != 0 ]
then
  echo 'Installing Sublime Text... see https://www.sublimetext.com/docs/3/linux_repositories.html'
  wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
  apt-get install apt-transport-https
  echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
  apt update
  apt install sublime-text
else
  echo 'Sublime Text is already installed.'
fi

# Install Arduino
if [ -f "/bin/arduino" ]
then
  echo 'Arduino IDE is already installed, probably.'
else
  echo 'Installing Arduino IDE'
  apt update
  apt install arduino
fi

# Install package manager for Sublime Text --I think this is an old version of package manager, instead use command pallette to install package manager
# if [ ! -e ~/.config/sublime-text-3/Installed\ Packages/Package\ Control.sublime-package ]
# then
#   wget -P ~/.config/sublime-text-3/Installed\ Packages/ https://packagecontrol.io/Package%20Control.sublime-package
# else
#   echo 'Sublime Text package manager already installed'
# fi


# # Install Anki for Linux
# echo 'If you want Anki, you need to download the tar file now and place it in your ~/Downloads folder.'
# echo 'The tar file can be downloaded from here: https://apps.ankiweb.net/'
# # Prompt for a keypress to continue. Customise prompt with $*
# function pause {
#   >/dev/tty printf '%s' "${*:-Press any key to continue... }"
#   [[ $ZSH_VERSION ]] && read -krs  # Use -u0 to read from STDIN
#   [[ $BASH_VERSION ]] && </dev/tty read -rsn1
#   printf '\n'
# }
# pause
# anki -h
# if [ $? != 0 ]
# then
#   echo 'Installing Anki for Linux... see https://apps.ankiweb.net/'
#   tar xjf ~/Downloads/anki-2.1.14-linux-amd64.tar.bz2
#   mkdir ~/Programs
#   cd ~/Programs
#   cd anki-2.1.14-linux-amd64
#   make install
# else
#   echo 'Anki for Linux is already installed'
# fi


# Install KeePass2
# if [ ! -d keepass2 ]
# then
#   echo 'KeePass2 is already installed.'
# else
#   apt-add-repository ppa:jtaylor/keepass
#   apt update
#   apt install keepass2
# fi
