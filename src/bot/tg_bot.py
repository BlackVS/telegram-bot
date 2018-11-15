#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import argparse
import functools

## 3rd party
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import locks

# python-daemon not supports Windows
if not os.name == 'nt':
    import daemon

## my
import tg_settings
from tg_helpers import *

import tg_logger
import plugins

log    = tg_logger.log
logger = tg_logger.logger


flockm_name="{}/{}_botm.lock".format(tg_settings.tg_tmp_dir, tg_settings.tg_keyword)
flockd_name="{}/{}_botd.lock".format(tg_settings.tg_tmp_dir, tg_settings.tg_keyword)

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
        elif isinstance(r,tuple) and r[0]=="photo":
            with open(r[1], 'rb') as f:
                update.message.reply_photo(photo=f, timeout=50)
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
    # print(dir())

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

def bot():
    try:
        logger.debug("Checking if script already run...")
        logger.debug(" testing lock of "+flockd_name)
        f=os.open(flockd_name, os.O_TRUNC | os.O_CREAT | os.O_RDWR)
        fres=locks.lock(f, locks.LOCK_EX+locks.LOCK_NB)
        if fres:
            logger.debug(" bot is not active")
            main()
        else:
            logger.debug("Script already running...")
    except IOError:
        logger.debug("Bot is already running")
    except Exception as inst:
        logger.error(type(inst))
        logger.error(inst.args)
        logger.error(inst)
    else:
        logger.debug("Exiting script and unlocking")
        locks.unlock(f)
        os.close(f)
        os.remove(flockd_name)
    logger.debug("Bot is off...")

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(add_help=True, description='Telegram bot')
        parser.add_argument("-d", "--daemon", action="store_true", help="run as daemon, only Linux")
        parser.add_argument("-v", "--verbose", action="store_true", help="detailed/debug log")
        args = parser.parse_args()
        logger = tg_logger.initLogger(args.verbose)
        logger.debug("Checking if script already run...")
        logger.debug(" testing lock of "+flockm_name)
        fm=os.open(flockm_name, os.O_TRUNC | os.O_CREAT | os.O_RDWR)
        fmres=locks.lock(fm, locks.LOCK_EX+locks.LOCK_NB)
        if fmres: #main is not run
            logger.debug(" check if daemon is run: "+flockd_name)
            fd=os.open(flockd_name, os.O_TRUNC | os.O_CREAT | os.O_RDWR)
            fdres=locks.lock(fd, locks.LOCK_EX+locks.LOCK_NB)
            if fdres: #not run - unlock and re-run as daemon
                locks.unlock(fd) 
                logger.debug("dAemonize bot...")
                if args.daemon:
                    if os.name == 'nt':
                        logger.warning("daemon mode is not supported in Windows")
                    else:
                        with daemon.DaemonContext(files_preserve=tg_logger.logger_handlers):
                            bot()
                else:
                    bot()
            locks.unlock(fm)
        else:
            logger.debug("main is already running. Exiting")
    except IOError:
        logger.debug("Bot is already running")
    except Exception as inst:
        logger.error(type(inst))
        logger.error(inst.args)
        logger.error(inst)
