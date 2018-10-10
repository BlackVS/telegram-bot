import json, os
from ..plugincore import *
try:
    from .zabbixconnector import ZabbixConnector as ZBX
except Exception as inst:
    logger.error(type(inst))
    logger.error(inst.args)
    logger.error(inst)

@register_plugin("zbx","Zabbix plugin")
class ZabbixPlugin(PluginCore):

    def __init__(self, plugin_name, *args, **kwds):
        self.read_config(os.path.dirname(os.path.realpath(__file__)))

    @log
    @plugin_command("status", "get Zabbix server status", True, True)
    def cmd_status(self,object,cmd,options):
        if self.isSpecificObject(object):
            return ZBX.get_status(self.config[object])  # status of concrete server
        return None #invoke built-in all plugin call

    @log
    @plugin_command("list", "print list of monitored servers", True, False)
    def cmd_list_global(self,object,cmd,options):
        msg="Monitored servers:\n"
        for n,cfg in self.config.items():
            msg+="*{}* : {}:{} _{}_\n".format(n,cfg['name'],cfg['ip'],cfg['description'])
        return msg


    @log
    @plugin_command("dashboard", "access dashboards", False, True)
    def cmd_dashboard(self,object,cmd,options):
        if object in self.config:
            if not args:
                return ZBX.get_dashboard_list(self.config[object],options)
            else:
                return ZBX.get_dashboard(self.config[object],options)
        return cmd_not_impl(object,cmd)

    @log
    @plugin_command("graph", "access graphs", False, True )
    @plugin_subcommand("list", "get list of available graphs" , "/graph list _options_", ZBX.graph_list)
    @plugin_subcommand("get",  "get specific graph by graphid", "/graph get id",         ZBX.graph_get) 
    @plugin_option("filter", "filter graphs by mask in name","-f", str)
    @plugin_option("cnt", "show only first X results", None, int, 10)
    def cmd_graph(self,object,cmd,options):
        return self.cmd_help(object,cmd)
    