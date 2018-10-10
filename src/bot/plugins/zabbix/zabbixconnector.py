from pyzabbix import ZabbixAPI

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
    def get_dashboard(cfg):
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
    def graph_list(cfg,args):
        zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])
        #v=zapi.api_version()
        res="*Available graphs:*\n"
        try:
            limit_cnt=int(args['cnt'])
            common_args={ 'templated':False, 'sortfield':'graphid' }
            graphs_cnt = int(zapi.graph.get(countOutput=True,**common_args))
            if graphs_cnt>limit_cnt:
                res+="_({} graphs, show only first {})_\n".format(graphs_cnt,limit_cnt)
            graphs=zapi.graph.get(output = 'extend',
                                  expandName = True,
                                  selectHosts = 'extend',
                                  limit = limit_cnt,
                                  **common_args
                                  )
        except Exception as inst:
            return "API not supports this feature"
        res+="\n".join( "{} : {} - {}".format(g['graphid'],g['hosts'][0]['host'], g['name']) for g in graphs )
        return res

    @staticmethod
    def graph_get(cfg,args):
        zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])
        #v=zapi.api_version()

			#method = "graph.get"
			#params = @{
			#	output = "extend"
			#	selectTemplates = "extend"
			#	selectHosts = @(
			#		"hostid",
			#		"name"
			#	)
			#	selectItems = "extend"
			#	selectGraphItems = "extend"
			#	selectGraphDiscovery = "extend"
			#	expandName = $expandName
			#	hostids = $HostID
			#	graphids = $GraphID
			#	templateids = $TemplateID
			#	itemids = $ItemID
			#	sortfield = "name"
			#}

        return res
