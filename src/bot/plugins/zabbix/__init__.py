import json, os
from ..plugincore import *
from .zabbixconnector import ZabbixConnector as ZBX

@register_plugin("zbx","Zabbix plugin")
class ZabbixPlugin(PluginCore):

    def __init__(self, plugin_name, *args, **kwds):
        self.read_config(os.path.dirname(os.path.realpath(__file__)))

    @log
    @plugin_command("status",
                "get Zabbix server status",
                ("Usage:\n"
                 "`/zbx status` - status of all monitored Zabbix servers\n"
                 "`/zbx status server` - status of specific server\n"
                ),
                True, 
                True)
    def cmd_status(self,object,cmd,args=None):
        if object in self.config:
            return ZBX.get_status(self.config[object])
        return self.cmd_not_impl(object,cmd,args)

    @log
    @plugin_command("list",
                "print list of monitored servers",
                ("Usage:\n"
                 "`/zbx list` - list of all monitored Zabbix servers\n"
                ),
                True, 
                False)
    def cmd_list(self,object,cmd,args=None):
        msg="Monitorred servers:\n"
        for n,cfg in self.config.items():
            msg+="*{}* : {}:{} _{}_\n".format(n,cfg['name'],cfg['ip'],cfg['description'])
        return msg


    @log
    @plugin_command("dashboard",
                "access dashboards",
                ("Usage:\n"
                 "`/zbx dashboard` - list of available dashboards\n"
                 "`/zbx dashboard id` - get specific dashboard\n"
                ),
                False, 
                True)
    def cmd_graph(self,object,cmd,args=None):
        if object in self.config:
            if not args:
                return ZBX.get_dashboard_list(self.config[object])
            else:
                return ZBX.get_dashboard(self.config[object],args)
        return cmd_not_impl(object,cmd,args)

