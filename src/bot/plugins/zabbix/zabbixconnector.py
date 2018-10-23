from pyzabbix import ZabbixAPI
import tg_settings
import requests

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

    #returns zapi and list of found graphs 
    @staticmethod
    def _get_graphs(cfg,args):
        try:
            zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])
            #v=zapi.api_version()
            graphs=None
            message=""

            limit_cnt=int(args['cnt'])
            common_args={ 'templated':False, 'sortfield':'graphid' }

            search={}
            if "filter_by_name" in args:
                search["name"]=args["filter_by_name"]
            if search:
                common_args["search"]=search

            filter={}
            if "filter_by_host" in args:
                filter["host"]=args["filter_by_host"]
            if filter:
                common_args["filter"]=filter

            graphs_cnt = int(zapi.graph.get(countOutput=True,**common_args))
            if graphs_cnt>limit_cnt:
                message+="_({} graphs, show only first {})_\n".format(graphs_cnt,limit_cnt)
            if graphs_cnt>0:
                graphs=zapi.graph.get(output = 'extend',
                                      expandName = True,
                                      selectHosts = 'extend',
                                      limit = limit_cnt,
                                      **common_args
                                      )
            else:
                message+="Not found"
        except Exception as inst:
            return (None,None)
        return (zapi,graphs,message)

    @staticmethod
    def _get_photo(cfg,zapi,graph_id,graph_width,graph_height,graph_period):
        fileURL = tg_settings.tg_tmp_dir + "/{0}.png".format(graph_id)
        zbx_img_url = cfg['url'] + "/chart2.php?graphid={0}&period={1}&width={2}&height={3}".format(graph_id, graph_period, graph_width, graph_height)
        ##
        requests.packages.urllib3.disable_warnings()
        data_api = {"name":cfg['api_user'], "password":cfg['api_pass'], "enter":"Sign in"}
        answer = requests.post( cfg['url'] + "/", 
                                data  =data_api, 
                                verify=False
                               )
        cookie = answer.cookies
        if len(answer.history) > 1 and answer.history[0].status_code == 302:
            return None
        if not cookie:
            return None

        answer = requests.get( zbx_img_url, 
                               cookies=cookie, 
                               verify =False, 
                               #auth=requests.auth.HTTPBasicAuth(cfg['api_user'],cfg['api_pass'])
                              )
        
        status_code = answer.status_code
        if status_code == 404:
            logger.error("Failed getting graph from Zabbix: {}".format(zbx_img_url))
            return None
        res_img = answer.content
        with open(fileURL, 'wb') as fp:
            fp.write(res_img)
        return fileURL


    @staticmethod
    def graph_list(cfg,args):
        zapi, graphs, message = ZabbixConnector._get_graphs(cfg,args)
        if not zapi:
            return "No conenction to Zabbix server"
        if not graphs:
            return "*Available graphs:* "+message

        #v=zapi.api_version()
        res_header="*Available graphs:*\n"+message
        res_body=""
        res_body+="\n".join( "{} : {} - {}".format(g['graphid'],g['hosts'][0]['host'], g['name']) for g in graphs )
        ##
        res_body=res_body.replace("_","\_")
        res_body=res_body.replace("*","\*")
        return res_header+res_body

    @staticmethod
    def graph_show(cfg,args):
        zapi, graphs, message = ZabbixConnector._get_graphs(cfg,args)
        if not zapi:
            return "No conenction to Zabbix server"
        if not graphs:
            return "*Available graphs:* "+message

        #if len(graphs)!=1:
        #    return "Must be only one!"
        return [ ("photo", ZabbixConnector._get_photo(cfg, zapi, g["graphid"], args['graph_width'], args['graph_height'], args['graph_period'])) for g in graphs ]
