#!/bin/bash

BOTDIR = tgbot
INSTALLDIR = /opt/$BOTDIR

@echo "Install bot to: $INSTALLDIR"
@echo "* creating folder: $INSTALLDIR"
sudo mkdir $INSTALLDIR
cd $INSTALLDIR

@echo "* cloning from git"
sudo git clone https://github.com/BlackVS/telegram-bot.git .
@echo "* switching to dev
sudo git checkout dev
@echo "* installing packages"
sudo apt install python3-pip -y
sudo pip3 install pipenv 
pipenv install --python 3
