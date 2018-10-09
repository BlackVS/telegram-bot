from ..plugincore import *

@register_plugin("ccr","RouterOS plugin")
class RouterOSPlugin(PluginCore):
    def __init__(self, *args, **kwds):
        pass

    @log
    @plugin_command("status", "get Mikrotik routers status", True, True)
    def cmd_status(self,object,cmd,args=None):
        return cmd_not_impl(object,cmd,args)

