import json, os
from ..plugincore import *
from .zabbixConnector import ZabbixConnector as ZBX

@register_plugin("zbx","Zabbix plugin")
class ZabbixPlugin(PluginCore):

    def __init__(self, plugin_name, *args, **kwds):
        self.read_config(os.path.dirname(os.path.realpath(__file__)))

    @log
    @plugin_command("help",
                "get detailed help for command",
                "",
                True, False)
    def cmd_help(self,object,cmd,args=None):
        return super().cmd_help(object,cmd,args)
    
    @log
    @plugin_command("status",
                "get Zabbix server status",
                ("Usage:\n"
                 "`/zbx status` - status of all monitored Zabbix servers\n"
                 "`/zbx status server` - status of specific server\n"
                ),
                True, True)
    def cmd_status(self,object,cmd,args=None):
        if object in self.config:
            return ZBX.get_status(self.config[object])
        res=""
        for name,cfg in self.config.items():
            res+=ZBX.get_status(cfg)
        return res
        #return ""

    @log
    @plugin_command("list",
                "print list of monitored servers",
                ("Usage:\n"
                 "`/zbx list` - list of all monitored Zabbix servers\n"
                ),
                True, False)
    def cmd_list(self,object,cmd,args=None):
        msg="Monitorred servers:\n"
        for n,cfg in self.config.items():
            msg+="*{}* : {}:{} _{}_\n".format(n,cfg['name'],cfg['ip'],cfg['description'])
        return msg

