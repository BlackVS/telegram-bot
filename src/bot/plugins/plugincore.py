from collections import defaultdict
from tg_helpers import *

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
## COMMANDS=defaultdict(lambda:None)

## own for each plugin module
def plugin_command(cmd,desc,help,f):
    def actual_decorator(func):
        mod = sys.modules[func.__module__]
        if not hasattr(mod, 'COMMANDS'):
            mod.COMMANDS = defaultdict(lambda:None)
        mod.COMMANDS[cmd]=(func,desc,help,f)
        return func
    return actual_decorator

class PluginCore:

    def __init__(self, *args, **kwds):
        pass

    def cmd_help(self,cmd,args=None):
        mod = sys.modules[self.__module__]
        if not hasattr(mod, 'COMMANDS'):
            return "No commands defined"

        if not args:
            msg="*Available commands:*\n"
            msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,f) in mod.COMMANDS.items() if f)
        else:
            p=mod.COMMANDS[args[0]]
            if not p:
                msg="Unknown `{args[0]}`".format()
            else:
                msg=p[2]
        return msg

    @log
    def process(self,plugin,cmd):
        if not cmd:
            return cmd_help()
        keywords=cmd.split()
        if len(keywords)==0:
            return cmd_help()

        mod = sys.modules[self.__module__]
        if not hasattr(mod, 'COMMANDS'):
            return "No commands defined"

        c=mod.COMMANDS[keywords[0]]
        if c==None:
            return "Unknown keyword `{}`".format(keywords[0])
        if 'help' in keywords[1:]:
            return self.cmd_help('help', [ keywords[0] ])
        return c[0](self,keywords[0],keywords[1:])