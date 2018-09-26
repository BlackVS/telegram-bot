from ..plugincore import *

@register_plugin("zbx","Zabbix plugin")
class ZabbixPlugin(PluginCore):
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
                "get Zabbix server status",
                ("Usage:\n"
                 "`/zbx status` - status of all monitored Zabbix servers\n"
                 "`/zbx status server` - status of specific server\n"
                ),
                True)

    def cmd_status(self,cmd,args=None):
        return "Not implemented"
