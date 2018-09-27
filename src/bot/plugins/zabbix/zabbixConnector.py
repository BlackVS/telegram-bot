from pyzabbix import ZabbixAPI

PRIORITIES=["   ", "INFO", "WARN", "AVER", "HIGH", "CRIT"]

class ZabbixConnector:
    @staticmethod
    def get_status(cfg):
        # Create ZabbixAPI class instance
        zapi = ZabbixAPI(url=cfg['url'], user=cfg['api_user'], password=cfg['api_pass'])

        ## Get all monitored hosts
        #result1 = zapi.host.get(monitored_hosts=1, output='extend')

        ## Get all disabled hosts
        #result2 = zapi.do_request('host.get',
        #                          {
        #                              'filter': {'status': 1},
        #                              'output': 'extend'
        #                          })

        ## Filter results
        #hostnames1 = [host['host'] for host in result1]
        #hostnames2 = [host['host'] for host in result2['result']]
        # res=zapi.do_request('problem.get', { "output": "extend" })
        # res=zapi.host.get(monitored_hosts=1, output='extend')


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

        #problems=zapi.do_request('problem.get', 
        #                     {  "output"     : "extend",
        #                        #"selectTags" : "extend",
        #                        #"selectHosts": ['Host','Name'],
        #                        "recent"     : "false",
        #                        "sortfield"  : ["eventid"],
        #                        "sortorder"  : "DESC"
        #                      }
        #                   )

        #res=problems['result']
        #if len(res):
        #    for p in problems['result']:
        #        event=zapi.item.get(eventids = [p["eventid"]],
        #                             selectHosts = ["host","name"], 
        #                             #select_alerts = "extend",
        #                             #selectTags = "extend",
        #                             output = ["lastvalue","name"], 
        #                             monitored = 1)
        #        print(event)


            #res = zapi.host.get(monitored_hosts=1, output='extend');
            #hosts=defaultdict(lambda:None)
            #for r in res:
            #    hosts[r['hostid']]=r
            #    print(r)
            #print(hosts)
            #print(problems)
            #for p in problems:
            #    print(">> {} /n {} /n".format(p,hosts[p.]))