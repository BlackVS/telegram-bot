#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, signal
#from collections import *
## 3rd party
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import locks

## my
import tg_settings
from tg_helpers import *

## plugins
import plugins


## Commands
COMMANDS=dict()
def command(cmd):
    def wrap(func):
        COMMANDS[cmd]=func
        return func
    return wrap

MESSAGE_HANDLER=None
def message_handler(func):
    global MESSAGE_HANDLER
    MESSAGE_HANDLER=func
    return func

@command("start")
@log
def cmd_start(bot, update):
    update.message.reply_text('Awaiting orders.')

@command("hi")
@log
def cmd_start(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.name))

@command("help")
@log
def cmd_help(bot, update):
    update.message.reply_text("I don't want to do that!")

@message_handler
@log
def cmd_echo(bot, update):
    update.message.reply_text("WHAT {} ???".format(update.message.text))

@command("shutdown")
@command("kill")
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



#def test():
#    # Create ZabbixAPI class instance
#    zapi = ZabbixAPI(url=tg_settings.zabbix_server, user=tg_settings.zabbix_api_user, password=tg_settings.zabbix_api_pass)

#    ## Get all monitored hosts
#    #result1 = zapi.host.get(monitored_hosts=1, output='extend')

#    ## Get all disabled hosts
#    #result2 = zapi.do_request('host.get',
#    #                          {
#    #                              'filter': {'status': 1},
#    #                              'output': 'extend'
#    #                          })

#    ## Filter results
#    #hostnames1 = [host['host'] for host in result1]
#    #hostnames2 = [host['host'] for host in result2['result']]
#    # res=zapi.do_request('problem.get', { "output": "extend" })
#    # res=zapi.host.get(monitored_hosts=1, output='extend')
#    triggers=zapi.trigger.get(  only_true = 1,
#                                filter = { 'value': 1 },
#                                skipDependent = 1,
#                                monitored = 1,
#                                active = 1,
#                                output = 'extend',
#                                #expandDescription = 1,
#                                #expandData = 'host',
#                                selectHosts=['host'],
#                                withLastEventUnacknowledged = 1
#                             )

#    problems=zapi.do_request('problem.get', 
#                         {  "output"     : "extend",
#                            #"selectTags" : "extend",
#                            #"selectHosts": ['Host','Name'],
#                            "recent"     : "false",
#                            "sortfield"  : ["eventid"],
#                            "sortorder"  : "DESC"
#                          }
#                       )

#    res=problems['result']
#    if len(res):
#        for p in problems['result']:
#            event=zapi.item.get(eventids = [p["eventid"]],
#                                 selectHosts = ["host","name"], 
#                                 #select_alerts = "extend",
#                                 #selectTags = "extend",
#                                 output = ["lastvalue","name"], 
#                                 monitored = 1)
#            print(event)
#        #res = zapi.host.get(monitored_hosts=1, output='extend');
#        #hosts=defaultdict(lambda:None)
#        #for r in res:
#        #    hosts[r['hostid']]=r
#        #    print(r)
#        #print(hosts)
#        #print(problems)
#        #for p in problems:
#        #    print(">> {} /n {} /n".format(p,hosts[p.]))

def main():
    #test()
    #print(plugins.zabbix.get_description())
    for n,p in plugins.items():
        msg="Plugin {}='{}' loaded".format(n,p.get_description())
        logger.warning(msg)
    return

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(tg_settings.botAPIkey)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    print(dir())

    for cmd,func in COMMANDS.items():
        dp.add_handler(CommandHandler(cmd, func))
    #dp.add_handler(CommandHandler("start", cmd_start))
    #dp.add_handler(CommandHandler("help", cmd_help))

    if MESSAGE_HANDLER:
        dp.add_handler(MessageHandler(Filters.text, MESSAGE_HANDLER))
    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, cmd_echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    #updater.start_polling(poll_interval = 1.0,timeout=20)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def initLogger():
        global logger
        global debug

        try:
            logger_name=getLoggerName()
            log_file = "{0}/{1}.log".format(tg_settings.tg_log_dir, logger_name)
            logging.basicConfig(level=(logging.INFO,logging.DEBUG)[debug])
            logger = logging.getLogger(logger_name)
            # create file handler which logs even debug messages
            # fh = logging.FileHandler(log_file)
            #if not os.path.isfile(log_file):
            #    touch(log_file)
            fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5, encoding=None, delay=0)
            fh.setLevel((logging.INFO,logging.DEBUG)[debug])
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(fh)
            logger.addHandler(ch)
            logger.debug("Starting Zbx2Tg script...")
        except Exception as inst:
            logger.warning("Failed to lock file: is seems to be script already running")
            #logger.error(type(inst))
            #logger.error(inst.args)
            #logger.error(inst)
            raise

if __name__ == '__main__':
    debug=False
    if hasattr(tg_settings,"debug"):
        debug=tg_settings.debug
    if "--debug" in sys.argv:
        debug=True

    fname="{}/{}_bot.lock".format(tg_settings.tg_tmp_dir, tg_settings.tg_keyword)
    try:
        initLogger()
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