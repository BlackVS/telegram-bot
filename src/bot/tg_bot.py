#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal

## 3rd party
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import locks

## my
import tg_settings
from tg_helpers import *

from tg_logger import *
import plugins


## Commands
## (func,help,show in help)
COMMANDS=dict()
def command(cmd,help,f):
    def wrap(func):
        COMMANDS[cmd]=(func,help,f)
        return func
    return wrap

    def decorator(func):
        COMMANDS[cmd]=(func,help,f)
        return func
    return decorator

def commandext(cmd,help,f):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(cmd,*args,**kwargs)
        COMMANDS[cmd]=(wrapper,help,f)
        return wrapper
    return actual_decorator

MESSAGE_HANDLER=None
def message_handler(func):
    global MESSAGE_HANDLER
    MESSAGE_HANDLER=func
    return func

@command("start","start conversation with bot",True)
@log
def cmd_start(bot, update):
    update.message.reply_text('Awaiting orders.')

@command("hi","greetings to bot",True)
@log
def cmd_start(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.name))

@message_handler
@log
def cmd_echo(bot, update):
    update.message.reply_text("WHAT {} ???".format(update.message.text))

@command("shutdown","shutdown bot",True)
@command("kill","shutdown bot",True)
@log
def cmd_shutdown(bot, update):
    update.message.reply_text('As you wish. Killing bot...')
    #os.kill(os.getpid(),signal.SIGINT)
    os.kill(os.getpid(),signal.SIGTERM)
    #os.kill(os.getpid(),signal.CTRL_BREAK_EVENT)
    
@log
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)

@command("plugins","work with plugins",True)
@log
def cmd_plugins(bot, update):
    msg="*Available plugins:*"
    for n,(p,d) in plugins.items():
        msg+="\n{}(_'{}'_)".format(n,d)
    update.message.reply_markdown(msg)
    return    

@commandext("help","get help on commands",True)
@log
def cmd_help(cmd, bot, update, *args, **kwargs):
    text=update.message.text[len(cmd)+1:].strip()
    if not text:
        msg="*Available commands:*\n"
        msg+=" ".join(cmd for cmd,(func,help,f) in COMMANDS.items() if f)
    else:
        if text=='full':
            msg="*Available commands:*\n"
            msg+="\n".join( "*{}* : {}".format(cmd,help) for cmd,(func,help,f) in COMMANDS.items() if f)
        elif not COMMANDS[text]:
            msg="Wrong command syntax\nUse */help*/ or */help command*"
        else:
            msg="*/{0}* : {1}. Run `/{0} help` to get detailed help on command usage".format(text,COMMANDS[text][1])
    update.message.reply_markdown(msg)
    return    

@log
def call_plugin(cmd, bot, update):
    plugin=plugins.get(cmd)
    if plugin==None:
        update.message.reply_markdown("Yep... not yet....")
        return
    text=update.message.text[len(cmd)+1:].strip()
    res=None
    try:
        res=plugin.process(cmd,text)
    except Exception as inst:
        #logger.warning("Failed to lock file: is seems to be script already running")
        logger.error(type(inst))
        logger.error(inst.args)
        logger.error(inst)
        update.message.reply_text("Failed to call plugin. Check logs")
        raise
    if not isinstance(res,list):
        res=[res]
    for r in res:
        if isinstance(r,str):
            update.message.reply_markdown(r)
        else:
            update.message.reply_markdown("Unsupported result: {}".format(type(r)))
    return    

def main():
    #test()

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(tg_settings.botAPIkey)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    print(dir())

    for cmd,(func,help,f) in COMMANDS.items():
        dp.add_handler(CommandHandler(cmd, func))

    #register plugins commands
    for n,(p,d) in plugins.items():
        #dp.add_handler(CommandHandler(n, call_plugin))
        dp.add_handler(CommandHandler(n, commandext(n,d,True)(call_plugin)))
        

    if MESSAGE_HANDLER:
        dp.add_handler(MessageHandler(Filters.text, MESSAGE_HANDLER))
    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, cmd_echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(timeout=0,read_latency=3.0)
    #updater.start_polling(poll_interval = 1.0,timeout=20)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


if __name__ == '__main__':
    fname="{}/{}_bot.lock".format(tg_settings.tg_tmp_dir, tg_settings.tg_keyword)
    try:
        logger.debug("Checking if script already run...")
        logger.debug(" testing lock of "+fname)
        with open(fname, 'wb') as f:
            if locks.lock(f, locks.LOCK_EX+locks.LOCK_NB):
                #with open(fname, 'wb') as ff:
                #    if not locks.lock(ff, locks.LOCK_EX+locks.LOCK_NB):
                #        exit(0)
                #Deamonize in Linux
                fStop = os.fork()!=0 if hasattr(os, 'fork') else False
                # fork()==0 - if child
                # in no fork (Windows) - just continue
                if fStop: 
                    # Running as daemon now. PID is fpid
                    logger.debug("Original process is shutdowning, child will continue")
                    sys.exit(0)
                logger.debug("Continue as daemon")
                main()
            else:
                logger.debug("Script already running...")
    except Exception as inst:
        logger.error(type(inst))
        logger.error(inst.args)
        logger.error(inst)
    finally:
        logger.debug("Exiting script and unlocking")
        os.remove(fname)
    logger.debug("Bot is off...")