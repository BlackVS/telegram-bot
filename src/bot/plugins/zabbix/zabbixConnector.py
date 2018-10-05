from pyzabbix import ZabbixAPI
import argparse

PRIORITIES=["   ", "INFO", "WARN", "AVER", "HIGH", "CRIT"]

WIDGETTYPE = { 
                    "actlog":  "Action log", 
                    "clock":  "Clock", 
                    "dataover":  "Data overview", 
                    "dscvry":  "Discovery status", 
                    "favgrph":  "Favourite graphs", 
                    "favmap":  "Favourite maps", 
                    "favscr":  "Favourite screens", 
                    "graph":  "Graph", 
                    "hoststat":  "Host status", 
                    "sysmap":  "Map", 
                    "navigationtree":  "Map Navigation Tree", 
                    "plaintext":  "Plain text", 
                    "problems":  "Problems", 
                    "stszbx":  "Status of Zabbix", 
                    "syssum":  "System status", 
                    "trigover":  "Trigger overview", 
                    "url":  "URL", 
                    "webovr":  "Web monitoring",
                }


class TGMarkupHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super().add_usage( usage, actions, groups, prefix)
    def _format_action(self, action):
            return super()._format_action(action)
    def _format_action_invocation(self, action):
        res=super()._format_action_invocation(action)
        return "`{}`".format(res)


class ZabbixConnector:
    @staticmethod
    def get_status(cfg):
        zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])

        triggers=zapi.trigger.get(  only_true = 1,
                                    filter = { 'value': 1 },
                                    skipDependent = 1,
                                    monitored = 1,
                                    active = 1,
                                    output = 'extend',
                                    expandDescription = 1,
                                    #expandData = 'host',
                                    selectHosts=['host'],
                                    withLastEventUnacknowledged = 1,
                                    sortfield = ["priority", "hostname", "lastchange"],
                                    sortorder = "DESC",
                                )
        res=""
        for t in triggers:
            p=int(t['priority'])
            res+="({}) *{}* :\n_{}_\n\n".format(PRIORITIES[p],t['hosts'][0]['host'],t['description'])
        return res

    @staticmethod
    def get_dashboard_list(cfg):
        zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])
        v=zapi.api_version()
        try:
            boards=zapi.dashboard.get(output = 'extend',
                                      selectWidgets = 'extend',
                                      selectUsers = 'extend',
                                      selectUserGroups = 'extend',
                                  )
        except Exception as inst:
            return "API not supports this feature"
        res="*Available dashboards:\n*"
        res+="\n".join( "{} : {}".format(b['dashboardid'],b['name']) for b in boards )
        return res

    @staticmethod
    def get_graph_list(object,cmd,cfg,args):
        zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])
        v=zapi.api_version()
        parser = argparse.ArgumentParser(prog="*/{} {}*".format(object,cmd),
                                         description="Invoke Zabbix graphs related commands",
                                         formatter_class=TGMarkupHelpFormatter
                                         )
        parser._optionals.title="*Options:*"
        parser.add_argument("-l","--list", action='store_true', help="get list of available graphs")


        if not args:
            res=parser.format_help()
            #format_usage
        res=res.replace('[','\[')
        #res=res.replace(']','\]')
        return res
