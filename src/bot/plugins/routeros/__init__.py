from ..plugincore import *

@register_plugin("ccr","RouterOS plugin")
class RouterOSPlugin(PluginCore):
    def __init__(self, *args, **kwds):
        pass

    @log
    @plugin_command("status",
                "get Mikrotik routers status",
                ("Usage:\n"
                 "`/ccr status` - status of all monitored routers\n"
                 "`/ccr status router` - status of specific router\n"
                ),
                True, True)
    def cmd_status(self,object,cmd,args=None):
        return self.cmd_not_impl(object,cmd,args)

