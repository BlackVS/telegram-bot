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
        mod.COMMANDS[cmd]=(func,desc,fAll,fObject)
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
                  desc,     # Command description
                  flags=None,    # None or list of flags like ['-l','--list']. 
                            # If none then "/object command option=value" or "/object command option value" style is used
                            # If it is then "/object command flag value" or "/object command flag=value" style used
                            # /zbx graph list -f=Windows
                            # /zbx graph list -f Windows
                            # /zbx graph list filter=Windows
                            # /zbx graph list filter Windows
                  arg_type=None, # None if just switch (in such case True or False will be), int, str, list of choices if value required
                  default_value=None, # None or default value
                 ):
    def wrapper(func):
        nonlocal flags
        if not hasattr(func, 'OPTIONS'):
            func.OPTIONS = dict()
        if isinstance(flags,str):
            flags=[flags]
        func.OPTIONS[option]=(desc,flags,arg_type,default_value)
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
        return  mod.COMMANDS

    def get_command(self,cmd):
        mod = sys.modules[self.__module__]
        if not hasattr(mod, 'COMMANDS'):
            return None
        return  mod.COMMANDS.get(cmd, (None,None,None,None))

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
        cmd_func,desc,fAll,fObject=self.get_command(cmd)
        if cmd_func==None:
            return "Unknown command `{}`".format(cmd)
        msg=("*Usage:*\n"
             "`/{} {} cmd options` , where\n\n"
             "*cmd* - subcommand:\n"
             .format(object,cmd)
             )
        
        if hasattr(cmd_func,'SUBCOMMANDS') and cmd_func.SUBCOMMANDS:
            for s,(hook,desc,help) in cmd_func.SUBCOMMANDS.items():
                msg+="` `_{}_ - {}\n".format(s,desc)

        if hasattr(cmd_func,'OPTIONS') and cmd_func.OPTIONS:
            msg+="\n*options* - subcommand options/modifiers:\n"
            for o,(desc,flags,arg_type,default_value) in cmd_func.OPTIONS.items():
                full_desc=desc
                if arg_type!=None:
                    full_desc="{}, _{}_".format(full_desc,arg_type.__name__)
                if default_value!=None:
                    full_desc="{}, by default {}".format(full_desc,default_value)
                msg+="\n{}:\n".format(full_desc)
                msg_suffix=""
                if arg_type!=None:
                    msg_suffix="`=`_value_"
                if flags:
                    msg+="".join( "` {}`".format(f)+msg_suffix for f in flags)
                else:
                    msg+="` {}`".format(o)+msg_suffix
                msg+="\n"
        return msg

    def cmd_help(self,object,cmd,args=None):
        #help for plugin/server
        if cmd=='help': 
            CMDS=self.get_commands()
            if not CMDS:
                return "No commands defined"
            msg="*Available commands:*\n"
            if object in self.config:
                #object specific commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,fAll,fObject) in CMDS.items() if fObject)
            else:
                #general plugin commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,fAll,fObject) in CMDS.items() if fAll)
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
            for o,(desc,flags,arg_type,default_value) in func.OPTIONS.items():
                if flags:
                    for f in flags:
                        (options_map1,options_map2)[bool(arg_type)][f]=o
                else:
                    (options_map1,options_map2)[bool(arg_type)][o]=o
                if default_value!=None:
                    options[o]=default_value
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

        cmd_key =keywords[0]
        cmd_args=keywords[1:]

        if cmd_key=='help': #built-in command, list all commands
            return self.cmd_help(object, cmd_key, cmd_args)

        cmd_func,desc,fAll,fObject=self.get_command(cmd_key)
        if cmd_func==None:
            return "Unknown command `{}`".format(cmd)
        
        if cmd_args and cmd_args[0]=='help':
            return self.cmd_help(object, cmd_key, ['help'])

        if not cmd_args and hasattr(cmd_func,'SUBCOMMANDS'):
            return self.get_cmd_help(object,cmd_key) #return help on subcommands

        ##parse args
        sub_cmd,args=self.parse_args(cmd_func,cmd_args)
        if isinstance(args,str): #error parsing
            return args

        #call to specific object
        if object in self.config and fObject:
            #call root command function if no subcommands defined
            if not hasattr(cmd_func, 'SUBCOMMANDS'):
                return cmd_func(self,object,cmd_key,args)

            #try call subcommand
            hook,*_=cmd_func.SUBCOMMANDS.get(sub_cmd,None)
            if hook!=None:
                return hook(self.config[object],args)
            return msgError

        #wide plugin call
        if (object not in self.config) and fAll:
            #call root command function if no subcommands defined
            if not hasattr(cmd_func, 'SUBCOMMANDS'):
                msg=cmd_func(self,object,cmd_key,cmd_args)
                if not msg:
                    return [cmd_func(self,srv,cmd_key,cmd_args) for srv in self.config]
                return msg
            #try call subcommand
            hook,*_=cmd_func.SUBCOMMANDS.get(sub_cmd,None)
            if hook!=None:
                msg=hook(self.config[object],args)
                if not msg:
                    return [hook(self.config[srv],args) for srv in self.config]
                return msg

        return msgError

