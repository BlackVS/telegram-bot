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

function run() { 
    # echo $@
    $@
    check
}

function print_h0(){
    echo -e "* ${WHITE}${BOLD} $@  ${NOBOLD}${NC}:"
}

function print_h1(){
    echo ""
    echo -n -e "* ${YELLOW} $@  ${NC}:"
}

print_h0 "Installing Telegram bot"

echo "Install bot to: $INSTALLDIR"

print_h1 "creating folder $INSTALLDIR"

run sudo mkdir $INSTALLDIR
run cd $INSTALLDIR

print_h1 "cloning from git"
run sudo git clone https://github.com/BlackVS/telegram-bot.git .

print_h1 "switching to dev"
run sudo git checkout dev

print_h1 "installing python3-pip"
run sudo apt -qqq install python3-pip -y

print_h1 "installing pipenv"
run sudo pip3 -q install pipenv 

print_h1 "initializing pipenv"
run pipenv --bare install --python 3
