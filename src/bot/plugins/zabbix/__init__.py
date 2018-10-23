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
    @plugin_subcommand("show","show graph/graphs", "/graph show _options_",         ZBX.graph_show) 
    @plugin_option("filter_by_host", "filter graphs by host name","host", str)
    @plugin_option("filter_by_name", "filter graphs by graph name","name", str)
    @plugin_option("cnt", "show only first X results", None, int, 10)
    @plugin_option("graph_width" , "show: graph width", "width" , int, 400)
    @plugin_option("graph_height", "show: graph height","height", int, 80)
    @plugin_option("graph_period", "show: graph period","period", int, 8*60*60)
    def cmd_graph(self,object,cmd,options):
        return self.cmd_help(object,cmd)
    