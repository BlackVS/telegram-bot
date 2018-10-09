import os
import json
import inspect
from tg_helpers import *
from tg_logger import *

## common for all plugin modules
def register_plugin(name,desc):
    def actual_decorator(plugin):
        mod = sys.modules[plugin.__module__]
        if not hasattr(mod, 'PLUGINS'):
            mod.PLUGINS = dict()
        mod.PLUGINS[name]=(plugin(name),desc)
        return plugin
    return actual_decorator

## each plugin has commands
def plugin_command(cmd,desc,fAll,fObject):
    def actual_decorator(func):
        mod = sys.modules[func.__module__]
        if not hasattr(mod, 'COMMANDS'):
            mod.COMMANDS = dict()
        mod.COMMANDS[cmd]=(func,desc,None,fAll,fObject)
        return func
    return actual_decorator

## each plugin command may have subcommands
def plugin_subcommand(subcmd,
                      desc,     # Command description
                      help,     # Examples of command usage
                      hook      # hook to process this command
                      ):
    def wrapper(func):
        if not hasattr(func, 'SUBCOMMANDS'):
            func.SUBCOMMANDS = dict()
        if hook:
            func.SUBCOMMANDS[subcmd]=(hook,desc,help)
        return func
    return wrapper #return wrapper - used only in declarations

## each plugin command may have subcommands
def plugin_option(option,   # option key/name
                  flags,    # None or list of flags like ['-l','--list']. 
                            # If none then "/object command option=value" or "/object command option value" style is used
                            # If it is then "/object command flag value" or "/object command flag=value" style used
                            # /zbx graph list -f=Windows
                            # /zbx graph list -f Windows
                            # /zbx graph list filter=Windows
                            # /zbx graph list filter Windows
                  arg_type, # None if just switch (in such case True or False will be), int, str, list of choices if value required
                  desc,     # Command description
                 ):
    def wrapper(func):
        nonlocal flags
        if not hasattr(func, 'OPTIONS'):
            func.OPTIONS = dict()
        if isinstance(flags,str):
            flags=[flags]
        func.OPTIONS[option]=(flags,arg_type,desc)
        return func
    return wrapper #return wrapper - used only in declarations

## helper
def cmd_not_impl(object,cmd,args=None):
    return "*{}* : `{}` not impelmented".format(object,cmd)


class PluginCore:
    config=dict()

    def get_commands(self):
        mod = sys.modules[self.__module__]
        if not hasattr(mod, 'COMMANDS'):
            return None
        return mod.COMMANDS

    #must be called from @plugin_command wrapped functions
    def get_subcommand(self,subcmd):
        caller=sys._getframe(1).f_code.co_name
        func=getattr(self,caller)
        return func.SUBCOMMANDS.get(subcmd,None) if func else None

    #True if it iz specific object, False - if its is wide plugin call
    #For example status - 
    #/plugin status - common status of all objects of plugin
    #/plugin list - list objects
    #/object status - status of specific object (server)
    def isSpecificObject(self,object):
        return object in self.config

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

    def get_cmd_help(self,object,cmd):
        if not cmd:
            return None
        CMDS=self.get_commands()
        if CMDS==None:
            return "No commands defined"
        p=CMDS[cmd]
        if not p:
            return "Unknown command `{}`".format(cmd)
        cmd_func,desc,help,fAll,fObject=p
        msg=("*Usage:*\n"
             "`/{} {} cmd options` , where\n\n"
             "*cmd* - subcommand:\n"
             .format(object,cmd)
             )
        
        if cmd_func.SUBCOMMANDS:
            for s,(hook,desc,help) in cmd_func.SUBCOMMANDS.items():
                msg+="` `_{}_ - {}\n".format(s,desc)

        if cmd_func.OPTIONS:
            msg+="\n*options* - subcommand options/modifiers:\n"
            for o,(flags,arg_type,desc) in cmd_func.OPTIONS.items():
                msg+="\n{}:\n".format(desc)
                if flags:
                    if arg_type:
                        msg+="".join( "` {}=`_value({})_\n".format(f,arg_type.__name__) for f in flags)
                    else:
                        msg+="".join( "` {}`\n".format(f) for f in flags)
                else:
                    if arg_type:
                        msg+="` {}=`_value({})_ \n".format(o,arg_type.__name__)
                    else:
                        msg+="` {}`\n".format(o)

        return msg

    def cmd_help(self,object,cmd,args=None):
        CMDS=self.get_commands()
        if CMDS==None:
            return "No commands defined"

        #help for plugin/server
        if cmd=='help': 
            msg="*Available commands:*\n"
            if object in self.config:
                #object specific commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,fAll,fObject) in CMDS.items() if fObject)
            else:
                #general plugin commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,fAll,fObject) in CMDS.items() if fAll)
        # help for specific object commands
        else: 
            return self.get_cmd_help(object,cmd)
        return msg

    @log
    def parse_args(self,func,terms):
        options=dict()
        options_map1=dict()
        options_map2=dict()
        if hasattr(func,"OPTIONS"):
            ### to-do: can be done once and globally
            for o,(flags,arg_type,desc) in func.OPTIONS.items():
                if flags:
                    for f in flags:
                        (options_map1,options_map2)[bool(arg_type)][f]=o
                else:
                    (options_map1,options_map2)[bool(arg_type)][o]=o
        subcmd =None
        for t in terms:
            pos=t.find("=")
            if pos>0:
                #key=value option
                key  =t[:pos].strip()
                #map ->
                mkey=options_map2.get(key,None)
                if mkey:
                    value=t[pos+1:].strip()
                    options[mkey]=value
                    continue
                return (None, "Wrong key `{}`".format(key))
            if options_map1.get(t,None):
                options[ options_map1[t] ] = True
                continue
            if subcmd==None:
                subcmd=t
                continue
            return (None, "Wrong token `{}`".format(t))
        return (subcmd,options)

    @log
    def process(self,object,cmd):
        if not cmd:
            return self.cmd_help(object,'help')

        keywords=cmd.split()
        if len(keywords)==0:
            return self.cmd_help(object,'help')

        msgError="Not supported"
        CMDS=self.get_commands()
        if not CMDS:
            return "No commands defined"

        cmd_key =keywords[0]
        cmd_args=keywords[1:]

        if cmd_key=='help': #built-in command, list all commands
            return self.cmd_help(object, cmd_key, cmd_args)

        c=CMDS.get(cmd_key,None)
        if c==None:
            return "Unknown keyword `{}`".format(cmd_key)
        
        if cmd_args and cmd_args[0]=='help':
            return self.cmd_help(object, cmd_key, ['help'])

        if object in self.config and c[4]:
            #local 
            if not cmd_args:
                return self.get_cmd_help(object,cmd_key) #return help on usage
            ##parse args
            sub_cmd,args=self.parse_args(c[0],cmd_args)
            if isinstance(args,str): #error parsing
                return args
            return c[0](self,object,cmd_key,sub_cmd,args)

        if (object not in self.config) and c[3]:
            #global
            msg=c[0](self,object,cmd_key,cmd_args)
            if not msg:
                return [c[0](self,srv,cmd_key,cmd_args) for srv in self.config]
            return msg

        return msgError

