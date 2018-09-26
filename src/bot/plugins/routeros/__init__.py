from ..plugincore import *

@register_plugin("ccr","RouterOS plugin")
class RouterOSPlugin(PluginCore):
    def __init__(self, *args, **kwds):
        pass

    @log
    @plugin_command("help",
                "get detailed help for command",
                "",
                True)
    def cmd_help(self,cmd,args=None):
        return super().cmd_help(cmd,args)

    @log
    @plugin_command("status",
                "get Mikrotik routers status",
                ("Usage:\n"
                 "`/ccr status` - status of all monitored routers\n"
                 "`/ccr status router` - status of specific router\n"
                ),
                True)

    def cmd_status(self,cmd,args=None):
        return "Not implemented"

