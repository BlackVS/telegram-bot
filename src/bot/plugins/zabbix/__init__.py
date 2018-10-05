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

    @log
    @plugin_command("graph", "access graphs",   
                    ("Usage:\n"
                     "`/zbx graph <subcmd> <options>` - invoke subcommands\n"
                    ),
                    False, True #only local
                    )
    @plugin_subcommand("list1", None, None, "get list 1 of available graphs", "/graph list1", ZBX.get_graph_list)
    @plugin_subcommand("list2", None, None, "get list 2 of available graphs", "/graph list2", ZBX.get_graph_list)
    @plugin_subcommand("list3", None, None, "get list 3 of available graphs", "/graph list3", ZBX.get_graph_list)
    @plugin_subcommand("get",  ["-g","--get"], int, "get specific graph by graphid", "/graph get id", None ) #ZBX.get_graph_get
    def cmd_graph(self,object,cmd,args=None):
        if not args:
            subcmd=help
        else:
            subcmd=args[0]
        if subcmd=='help':
            return self.cmd_help(object.cmd,args)

        #check if local command
        if object in self.config:
            return ZBX.get_graph(object,cmd,self.config[object],args)
        #call as global
        return ZBX.get_graph(object,cmd,self.config,args)