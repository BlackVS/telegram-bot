import os
import json
from collections import defaultdict
from tg_helpers import *
from tg_logger import *

## common for all plugin modules
def register_plugin(name,desc):
    def actual_decorator(plugin):
        mod = sys.modules[plugin.__module__]
        if not hasattr(mod, 'PLUGINS'):
            mod.PLUGINS = defaultdict(lambda:None)
        mod.PLUGINS[name]=(plugin(name),desc)
        return plugin
    return actual_decorator

## Commands
## (func,help,show in help)

COMMANDS_DIRECT=defaultdict(lambda:None)

## own for each plugin module
def plugin_command(cmd,desc,help,fAll,fObject):
    def actual_decorator(func):
        mod = sys.modules[func.__module__]
        if not hasattr(mod, 'COMMANDS'):
            mod.COMMANDS = defaultdict(lambda:None)
        mod.COMMANDS[cmd]=(func,desc,help,fAll,fObject)
        return func
    return actual_decorator

def cmd_not_impl(object,cmd,args=None):
    return "*{}* : `{}` not impelmented".format(object,cmd)


class PluginCore:
    config=dict()

    def get_commands(self):
        mod = sys.modules[self.__module__]
        if not hasattr(mod, 'COMMANDS'):
            return None
        return mod.COMMANDS

    def read_config(self, path):
        #read config
        try:
            logger.debug("Parsing config file (json)...")
            path=os.path.join(path,'config.json')
            with open(path) as f:
                self.config = json.load(f)
        except Exception as inst:
            logger.error(type(inst))
            logger.error(inst.args)
            logger.error(inst)
            self.config=None
            raise
        finally:
            logger.debug("JSON succesfully parsed.")
            for section,cfg in self.config.items():
                logger.debug("{} : {}".format(section,cfg))
            mod = sys.modules[self.__module__]
            for name,cfg in self.config.items():
                mod.PLUGINS[name]=( self, "Invoke direct commands to {}".format(cfg['name'] ) )

    def cmd_help(self,object,cmd,args=None):
        CMDS=self.get_commands()
        if CMDS==None:
            return "No commands defined"

        if not args:
            msg="*Available commands:*\n"
            if object in self.config:
                #object specific commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,fAll,fObject) in CMDS.items() if fObject)
            else:
                #general plugin commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,fAll,fObject) in CMDS.items() if fAll)
        else:
            p=CMDS[args[0]]
            if not p:
                msg="Unknown `{args[0]}`".format()
            else:
                msg=p[2]
        return msg

    @log
    def process(self,object,cmd):
        if not cmd:
            return cmd_help(self,object,'help')
        keywords=cmd.split()
        if len(keywords)==0:
            return cmd_help(self,object,'help')

        msgError="Not supported"
        CMDS=self.get_commands()
        if not CMDS:
            return "No commands defined"

        cmd_key =keywords[0]
        cmd_args=keywords[1:]

        if cmd_key=='help': #built-in command, list all commands
            return self.cmd_help(object, cmd_key, cmd_args)

        c=CMDS[cmd_key]
        if c==None:
            return "Unknown keyword `{}`".format(cmd_key)
        
         
        if object in self.config and c[4]:
            return c[0](self,object,cmd_key,cmd_args)

        if c[3]:
            return [ c[0](self,srv,cmd_key,cmd_args) for srv in self.config]

        return msgError