import json, os
from ..plugincore import *
from .zabbixconnector import ZabbixConnector as ZBX

@register_plugin("zbx","Zabbix plugin")
class ZabbixPlugin(PluginCore):

    def __init__(self, plugin_name, *args, **kwds):
        self.read_config(os.path.dirname(os.path.realpath(__file__)))

    @log
    @plugin_command("status", "get Zabbix server status", True, True)
    def cmd_status(self,object,cmd,args=None):
        if self.isSpecificObject(object):
            return ZBX.get_status(self.config[object])  # status of concrete server
        return None #invoke built-in all plugin call

    @log
    @plugin_command("list", "print list of monitored servers", True, False)
    def cmd_list_global(self,object,cmd,args=None):
        msg="Monitorred servers:\n"
        for n,cfg in self.config.items():
            msg+="*{}* : {}:{} _{}_\n".format(n,cfg['name'],cfg['ip'],cfg['description'])
        return msg


    @log
    @plugin_command("dashboard", "access dashboards", False, True)
    def cmd_dashboard(self,object,cmd,args=None):
        if object in self.config:
            if not args:
                return ZBX.get_dashboard_list(self.config[object])
            else:
                return ZBX.get_dashboard(self.config[object],args)
        return cmd_not_impl(object,cmd,args)

    @log
    @plugin_command("graph", "access graphs", False, True )
    @plugin_subcommand("list", "get list of available graphs" , "/graph list _options_", ZBX.graph_list)
    @plugin_subcommand("get",  "get specific graph by graphid", "/graph get id",         ZBX.graph_get) 
    @plugin_option("filter", "-f", str, "filter graphs by mask in name")
    #@plugin_option("filter", ["-f","--filter"], str, "filter graphs by mask in name")
    #@plugin_option("filter1", ["-f"], None, "filter graphs by mask in name")
    #@plugin_option("filter2", None, str, "filter graphs by mask in name")
    #@plugin_option("cnt", None, int, "only first X results, by default 10")
    def cmd_graph(self,object,cmd,subcmd,args=None):
        if not subcmd:
            subcmd='help'
        if subcmd=='help':
            return self.cmd_help(object,cmd)

        #get graphs for specific server
        if self.isSpecificObject(object):
            p=self.get_subcommand(subcmd)
            if not p:
                return cmd_not_impl(object,cmd,args)
            res=p[0](object,cmd,self.config[object],args)
            return res if res!=None else cmd_not_impl(object,cmd,args)
        #call as global
        return cmd_not_impl(object,cmd,args) #not supported as wide plugin command