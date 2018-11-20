#!/bin/bash

sudo echo "Install GIT realted staff"

WHITE='\033[1;37m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m'
BOLD="\e[1m"
NOBOLD="\e[21m"

onerror() {
    echo " FAILED, aborting script"
    exit 1
}

trap 'onerror' ERR

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAIL${NC}, aborting script"
        exit 1
    fi
}

function print_h0(){
    echo -e "* ${WHITE}${BOLD} $@  ${NOBOLD}${NC}: "
}

function print_h1(){
    echo ""
    echo -n -e "* ${YELLOW} $@  ${NC}: "
}

function run() { 
    print_h1 $1
    echo ${@:2}
    ${@:2}
    check
}

print_h0 "Installing git stuff"

#sudo apt update
#sudo apt -y upgrade

read -p 'GIT commit Username: ' UNAME
read -p 'GIT commit EMAIL: ' EMAIL

run "Install aps" sudo apt -y install git-core fonts-powerline zsh

print_h1 "Install zsh staff for local"
sh -c "$(wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O -)"
check

print_h1 "Install zsh staff for root"
sudo su -c sh -c "$(wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O -)"
check

cmd="git config --global user.name $UNAME"
echo $cmd
$cmd
sudo su -c "$cmd"

cmd="git config --global user.email $EMAIL"
echo $cmd
$cmd
sudo su -c "$cmd"

perl -i -pe 's!^(ZSH_THEME\s*=\s*).*!\1"agnoster"!; s!^(plugins\s*=[\s\n]*\([\s\n]*).*!\1 gitfast!' ~/.zshrc
#chsh -s $(which zsh)
