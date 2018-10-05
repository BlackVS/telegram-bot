import os
import json
import argparse
from tg_helpers import *
from tg_logger import *

#class TGMarkupHelpFormatter(argparse.HelpFormatter):
class TGMarkupHelpFormatter(argparse.RawTextHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super().add_usage( usage, actions, groups, prefix)
    def _format_action(self, action):
            return super()._format_action(action)
    def _format_action_invocation(self, action):
        res=super()._format_action_invocation(action)
        return "`{}`".format(res)

## common for all plugin modules
def register_plugin(name,desc):
    def actual_decorator(plugin):
        mod = sys.modules[plugin.__module__]
        if not hasattr(mod, 'PLUGINS'):
            mod.PLUGINS = dict()
        mod.PLUGINS[name]=(plugin(name),desc)
        return plugin
    return actual_decorator

## Commands
## (func,help,show in help)

COMMANDS_DIRECT=dict()


## own for each plugin module\
def plugin_command(cmd,desc,help,fAll,fObject):
    def actual_decorator(func):
        #@functools.wraps(func)
        #def wrapper(func):
        #    return func
        mod = sys.modules[func.__module__]
        if not hasattr(mod, 'COMMANDS'):
            mod.COMMANDS = dict()
        mod.COMMANDS[cmd]=(func,desc,help,fAll,fObject)
        #return wrapper
        return func
    return actual_decorator

def plugin_subcommand(subcmd,
                      flags, # None or list of flags like ['-l','--list']
                      arg_type, # None if just switch, int, str, list of choices if value required
                      desc, # "Comands is to bla-bla-bla"
                      help, # "Usage examples"
                      hook  # hook to process this command
                      ):
    def wrapper(func):
        if not hasattr(func, 'SUBCOMMANDS'):
            func.SUBCOMMANDS = dict()
        if hook:
            func.SUBCOMMANDS[subcmd]=(hook,flags,arg_type,desc,help)
        return func
    return wrapper #return wrapper - used only in declarations

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

        if not args or cmd=='help': #help for object
            msg="*Available commands:*\n"
            if object in self.config:
                #object specific commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,fAll,fObject) in CMDS.items() if fObject)
            else:
                #general plugin commands
                msg+="\n".join( "*{}* : {}".format(c,desc) for c,(func,desc,help,fAll,fObject) in CMDS.items() if fAll)
        else: #help for object commands
                #get subcommand help
            subcmd=args[0]
            p=CMDS[cmd]
            if not p:
                return "Unknown command `{}`".format(cmd)
            cmd_func,desc,help,fAll,fObject=p
            pp=cmd_func.SUBCOMMANDS.get(subcmd,None)
            if pp: #custom help for commands
                if object in self.config: #call local help
                    return pp(config,object,cmd,args)
                return cmd_not_impl(object,cmd,args)
            ### defaultgenerated  help on commands
            parser = argparse.ArgumentParser(prog="*/{} {}*".format(object,cmd),
                                             description="Invoke `{}` related commands".format(cmd),
                                             formatter_class=argparse.RawTextHelpFormatter,
                                             add_help=False
                                            )
            parser._optionals.title="*Options:*"
            parser._positionals.title="*Commands:*"
            #hook,keys,arg_type,desc,usage
            subcommands=[]
            for subcmd,(hook,flags,arg_type,desc,usage) in cmd_func.SUBCOMMANDS.items():
                if not flags:
                    subcommands.append(subcmd)
                    #parser.add_argument( subcmd, help=desc, required=False )
                else:
                    if arg_type==None: #just switch
                        parser.add_argument( *flags, action='store_true', help=desc)
                    else:
                        parser.add_argument( *flags, help=desc, type=arg_type)
            if subcommands:
                parser.add_argument( "_cmd_", help=" - one of next subbcommands:{0}" )
                subcommands.sort()
            msg=parser.format_help()
            msg=msg.replace('[','\[')

            msg=msg.replace("{0}", "\n"+"".join( "`  {}` - {}\n".format(s,cmd_func.SUBCOMMANDS[s][3]) for s in subcommands))

            #res=res.replace(']','\]')
        return msg

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
        
        if not cmd_args or cmd_args[0]=='help':
            return self.cmd_help(object, cmd_key, ['help'])

        if object in self.config and c[4]:
            return c[0](self,object,cmd_key,cmd_args)

        if c[3]:
            return [ c[0](self,srv,cmd_key,cmd_args) for srv in self.config]

        return msgError