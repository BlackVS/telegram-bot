#!/bin/bash
UNAME="BlackVS"
EMAIL="vvs@polesye.com"

sudo apt -y install git-core zsh
sudo apt -y install fonts-powerline

cmd="wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O -"
#for current user
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
$cmd | zsh

#for root
#sudo su -c 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"'
sudo su -c "$cmd | zsh"

cmd="git config --global user.name $UNAME"
#echo $cmd
$cmd
sudo su -c "$cmd"

cmd="git config --global user.email $EMAIL"
#echo $cmd
$cmd
sudo su -c "$cmd"

perl -i -pe 's!^(ZSH_THEME\s*=\s*).*!\1"agnostic"!; s!^(plugins\s*=[\s\n]*\([\s\n]*).*!\1 gitfast!' ~/.zshrc
#chsh -s $(which zsh)
