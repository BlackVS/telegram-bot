#!/bin/bash

sudo echo Installing Telegram bot

BOTDIR=tgbot
INSTALLDIR=/opt/$BOTDIR

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
    #echo -n \
    ${@:2}
    check
}

print_h0 "Installing Telegram bot"
print_h0 "Install bot to: $INSTALLDIR"

run "Creating folder $INSTALLDIR" \
sudo mkdir $INSTALLDIR

run "Entering $INSTALLDIR" \
cd $INSTALLDIR

run "cloning from git" \
sudo git clone https://github.com/BlackVS/telegram-bot.git .

run "switching to dev" \
sudo git checkout dev

run "installing python3-pip" \
sudo apt-get -qq install python3-pip -y

run "installing pipenv" \
sudo pip3 -q install pipenv 

run "initializing pipenv" \
pipenv --bare install --python 3
