#!/bin/bash

BOTDIR=tgbot
INSTALLDIR=/opt/$BOTDIR

onerror() {
    echo " FAILED, aborting script"
    exit 1
}

trap 'onerror' ERR

check() {
    if [ $? -eq 0 ]; then
        echo OK
    else
        echo FAIL, aborting script
        exit 1
    fi
}

function run() { 
    # echo $@
    $@
    check
}

echo "Install bot to: $INSTALLDIR"

echo -n "* creating folder $INSTALLDIR : "

run sudo mkdir $INSTALLDIR
run cd $INSTALLDIR

echo "* cloning from git"
run sudo git clone https://github.com/BlackVS/telegram-bot.git .

echo "* switching to dev"
run sudo git checkout dev

echo "* installing python3-pip"
run sudo apt install python3-pip -y

echo "* installing pipenv"
run sudo pip3 install pipenv 

echo "* initializing pipenv"
run pipenv install --python 3
