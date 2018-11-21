#!/bin/bash

sudo echo

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
    echo -e "* ${YELLOW} $@  ${NC}: "
}

function print_h1n(){
    echo ""
    echo -n -e "* ${YELLOW} $@  ${NC}: "
}

function run() { 
    print_h1n $1
    #echo -n \
    ${@:2}
    check
}

print_h0 "Installing Telegram bot"
print_h0 "Install bot to: $INSTALLDIR"

run "Creating folder $INSTALLDIR" \
sudo mkdir $INSTALLDIR

run "cloning from git" \
sudo git clone https://github.com/BlackVS/telegram-bot.git $INSTALLDIR

run "Entering $INSTALLDIR" \
cd $INSTALLDIR

run "switching to dev" \
sudo git checkout dev

run "installing python3-pip" \
sudo apt-get -qq install python3-pip -y 1>/dev/null

run "installing dependencies" \
sudo pip3 -q install -r requirements.txt

run "creating nologin user tgbot" \
sudo adduser tgbot --system --no-create-home --disabled-login --group

run "creating folder /var/log/tgbot" \
sudo mkdir /var/log/tgbot

run "chown /var/log/tgbot by tgbot user" \
sudo chown -R tgbot:tgbot /var/log/tgbot

run "creating folder /tmp/tgbot" \
sudo mkdir /tmp/tgbot

run "chown /tmp/tgbot by tgbot user" \
sudo chown -R tgbot:tgbot /tmp/tgbot

print_h0 "Please edit config files:"
print_h1 " $INSTALLDIR/src/bot/tg_settings.py"
print_h1 " $INSTALLDIR/src/bot/plugins/zabbix/config.json"

print_h0 "To check config run bot in verbose console mode:"
print_h1 " sudo -u tgbot python3 ./src/bot/tg_bot.py -v"
echo " Check output and try run command /help in bot chat in Telegram"
print_h0 "To run in daemon mode:"
print_h1 " sudo -u tgbot python3 ./src/bot/tg_bot.py -d"
