#!/usr/bin/env python
# coding: utf-8
import os
import sys
import requests
import logging
import logging.handlers
import json
import copy
from collections import defaultdict
#
import zbxtg_settings


logger = None

COLORS = [
   ("e6194b", "Red"),	     
   ("3cb44b", "Green"),
   ("ffe119", "Yellow"),
   ("0082c8", "Blue"),
   ("f58231", "Orange"), 
   ("911eb4", "Purple"),
   ("46f0f0", "Cyan"),
   ("f032e6", "Magenta"),
   ("d2f53c", "Lime"),
   ("fabebe", "Pink"),
   ("008080", "Teal"),
   ("e6beff", "Lavender"),
   ("aa6e28", "Brown"),
   ("fffac8", "Beige"),
   ("800000", "Maroon"),
   ("aaffc3", "Mint"),
   ("808000", "Olive"),
   ("ffd8b1", "Coral"),
   ("000080", "Navy"),
   ("808080", "Grey"),
   ("FFFFFF", "White"),
   ("000000", "Black")
]

TG_MSG_MODE_MARKDOWN="Markdown"
TG_MSG_MODE_HTML="HTML"
TG_MSG_MODES = [None, "None", TG_MSG_MODE_HTML, TG_MSG_MODE_MARKDOWN]

class Settings:
    msg_mode=None
    disable_web_page_preview=False
    disable_notification=False
    graph_width  = 0
    graph_height = 0
    graph_period = 0
    msg_subject_format_HTML ="{0}"
    msg_subject_format_Markdown ="{0}"

    def __init__(self):
        self.msg_mode = zbxtg_settings.msg_mode
        self.msg_subject_format_HTML = zbxtg_settings.msg_subject_format_HTML
        self.msg_subject_format_Markdown = zbxtg_settings.msg_subject_format_Markdown
        self.disable_web_page_preview = zbxtg_settings.disable_web_page_preview
        self.disable_notification = zbxtg_settings.disable_notification
        self.graph_width  = zbxtg_settings.graph_width
        self.graph_height = zbxtg_settings.graph_height
        self.graph_period = zbxtg_settings.graph_period

    def update(self,params):
        self.msg_mode=params.get("msg_mode",self.msg_mode)
        self.msg_subject_format_HTML    =params.get("msg_subject_format_HTML",    self.msg_subject_format_HTML)
        self.msg_subject_format_Markdown=params.get("msg_subject_format_Markdown",self.msg_subject_format_Markdown)
        self.disable_web_page_preview=params.get("disable_web_page_preview",self.disable_web_page_preview)
        self.disable_notification=params.get("disable_notification",self.disable_notification)
        self.graph_width =params.get("width" ,self.graph_width)
        self.graph_height=params.get("height",self.graph_height)
        self.graph_period=params.get("period",self.graph_period)

settings = Settings()

class ZabbixAPI:
    def __init__(self, server, username, password):
        self.server   = server
        self.username = username
        self.password = password
        self.verify   = zbxtg_settings.zabbix_api_verify
        self.cookie = None

    def login(self):
        if not self.verify:
            requests.packages.urllib3.disable_warnings()

        data_api = {"name": self.username, "password": self.password, "enter": "Sign in"}
        answer = requests.post( self.server + "/", 
                                data  =data_api, 
                                verify=self.verify,
                                #auth=requests.auth.HTTPBasicAuth(self.basic_auth_user, self.basic_auth_pass)
                               )
        cookie = answer.cookies
        if len(answer.history) > 1 and answer.history[0].status_code == 302:
            logger.warning("URL redirection happened (302)")
        if not cookie:
            logger.error("Authorization to Zabbix server failed, url: {0}".format(self.server + "/"))
            cookie = None

        self.cookie = cookie

    def graph_get(self, itemids, period, title, width, height):

        fileURL = zbxtg_settings.zbxtg_tmp_dir + "/{0}.png".format("-".join(map(str,itemids)))

        title = requests.utils.quote(title)

        drawtype = 5
        if len(itemids) > 1:
            drawtype = 2

        zbx_img_url_itemids = []
        for i,ids in enumerate(itemids):
            itemid_url = "&items[{0}][itemid]={1}&items[{0}][sortorder]={0}&items[{0}][drawtype]={3}&items[{0}][color]={2}".format(i, ids, COLORS[i], drawtype)
            zbx_img_url_itemids.append(itemid_url)

        zbx_img_url = self.server + "/chart3.php?period={0}&name={1}&width={2}&height={3}&graphtype=0&legend=1".format(period, title, width, height)
        zbx_img_url += "".join(zbx_img_url_itemids)

        logger.debug("Getting prath from Zabbix: {}".format(zbx_img_url))
        answer = requests.get( zbx_img_url, 
                               cookies=self.cookie, 
                               verify=self.verify, 
                               #auth=requests.auth.HTTPBasicAuth(self.basic_auth_user, self.basic_auth_pass)
                              )
        
        status_code = answer.status_code
        if status_code == 404:
            logger.error("Failed getting graph from Zabbix: {}".format(zbx_img_url))
            return None
        res_img = answer.content
        logger.debug("Saving Zabbix graph as {}".format(fileURL))
        with open(fileURL, 'wb') as fp:
            fp.write(res_img)
        return fileURL

    def api_test(self):
        headers = {'Content-type': 'application/json'}
        api_data = json.dumps({"jsonrpc": "2.0", "method": "user.login", "params":
                              {"user": self.username, "password": self.password}, "id": 1})
        api_url = self.server + "/api_jsonrpc.php"
        api = requests.post(api_url, data=api_data, proxies=self.proxies, headers=headers)
        return api.text


class TelegramAPI:
    tg_api_url   = "https://api.telegram.org/bot"
    tg_botAPIkey = None
    last_result  = None
    
    def __init__(self, key):
        self.tg_botAPIkey = key

    def httpGet(self, url):
        answer = requests.get(url)
        return answer.json()

    def getAPI(self):
        return  self.tg_api_url + self.tg_botAPIkey

    def formatMsgAsHTML(self,subject,text="",separator=" : "):
        global settings
        format=settings.msg_subject_format_HTML+separator+"{1}"
        return format.format(subject,text,separator)

    def formatMsgAsMarkdown(self,subject,text="",separator=" : "):
        global settings
        format=settings.msg_subject_format_Markdown+separator+"{1}"
        return format.format(subject,text,separator)


    def getPhotoFromZabbix(self,params):
        global settings

        #try get image from Zabbix
        zbx = ZabbixAPI(zbxtg_settings.zabbix_server, zbxtg_settings.zabbix_api_user, zbxtg_settings.zabbix_api_pass)
        zbx.login()
        if not zbx.cookie:
            logger.error("Failed to login to Zabbix web API")
            return None
        imageFile = zbx.graph_get( [params  ["itemid"]],
                                    settings.graph_period,
                                    params  ["title"],
                                    settings.graph_width,
                                    settings.graph_height)
        return imageFile

    def sendMessage(self, to, subject, text):
        global logger
        global settings
        #text=textIn.copy()

        messages=[]

        keyword=zbxtg_settings.zbxtg_keyword+":"
        text=text.strip()
        while text:
            i_pos=text.find(keyword)
            if i_pos==-1:
                messages.append( ("text", text.strip()) )
                text=""
            else:
                if i_pos>0:
                    messages.append( ("text", text[:i_pos].strip()) )
                    text=text[i_pos:]

                # text = "zbxtg:token={json}RestOfText"
                i_token=text.find("=")
                token     =text[len(keyword):i_token]
                token_s = text.find("{")
                token_e = text.find("}")+1
                token_text=text[token_s:token_e]
                
                logger.debug("Message token: {}".format(token) )
                logger.debug("Message json : {}".format(token_text) )

                try:
                    logger.debug("Parsing message json...")
                    params=json.loads(token_text)
                except Exception as inst:
                    logger.error(type(inst))
                    logger.error(inst.args)
                    logger.error(inst)
                    raise
                finally:
                    logger.debug("JSON succesfully parsed.")
                    logger.debug("= {}".format(params))

                if token=="graph":
                    messages.append( ("graph",params) )
                elif token=="options":
                    settings.update(params)
                else:
                    logger.debug("Error parsing parameters: unknown token = {}".format(token))
                    return False
                text=text[token_e:].strip()

        #send
        for token,params in messages:
            settings_backup=copy.copy(settings)
            if token=="text":
                if not self.sendMessageText(to, subject, params):
                    return False
            if token=="graph":
                settings.update(params)
                imageURL=self.getPhotoFromZabbix(params)
                if imageURL:
                    if not self.sendPhoto(to,subject,imageURL):
                        return False
                #clear temp image file
                os.remove(imageURL)
            settings=settings_backup
        return True

    def sendPhoto(self, to, subject, imageURL):
        global settings

        logger.debug("Send photo")
        logger.debug("      to: {}".format(to))
        logger.debug(" subject: {}".format(subject))
        logger.debug("imageURL: {}".format(imageURL))


        mode=settings.msg_mode
        if mode==TG_MSG_MODE_HTML:
            subject=self.formatMsgAsHTML(subject,separator="")
        elif mode==TG_MSG_MODE_MARKDOWN:
            subject=self.formatMsgAsMarkdown(subject,separator="")
        else:
            pass
        
        # https://core.telegram.org/bots/api#sendphoto
        url = self.getAPI() + "/sendPhoto"
        params = { "chat_id": to, 
                   "caption": subject, 
                   "disable_notification": settings.disable_notification,
                 }
        if mode==TG_MSG_MODE_HTML or mode==TG_MSG_MODE_MARKDOWN:
            params["parse_mode"]=mode

        files = {"photo": open(imageURL, 'rb')}
        answer = requests.post(url, params=params, files=files)
        self.last_result = answer
        res=answer.status_code == 200
        logger.debug("HTTP return code: {}".format(answer.status_code))
        if not res:
            logger.error("HTTP code: {}".format(answer.status_code))
            logger.error("     desc: {}".format(answer.text))
            logger.error(answer)
        return res

    def sendMessageText(self, to, subject, text):
        global settings
        logger.debug("Send simple text")
        logger.debug("      to: {}".format(to))
        logger.debug(" subject: {}".format(subject))
        logger.debug("    text: {}".format(text))

        url = self.getAPI() + "/sendMessage"
        
        mode=settings.msg_mode
        if mode==TG_MSG_MODE_HTML:
            message=self.formatMsgAsHTML(subject,text)
        elif mode==TG_MSG_MODE_MARKDOWN:
            message=self.formatMsgAsMarkdown(subject,text)
        else:
            message = "[{0}]:\n{1}".format(subject,text)

        ## https://core.telegram.org/bots/api
        params = {"chat_id": to,
                  "text"   : message, 
                  "disable_web_page_preview": settings.disable_web_page_preview, 
                  "disable_notification"    : settings.disable_notification, 
                 }
        if mode==TG_MSG_MODE_HTML or mode==TG_MSG_MODE_MARKDOWN:
            params["parse_mode"]=mode

        answer = requests.post(url, params=params)
        self.last_result = answer
        res=answer.status_code == 200
        logger.debug("HTTP return code: {}".format(answer.status_code))
        if not res:
            logger.error("HTTP code: {}".format(answer.status_code))
            logger.error("     desc: {}".format(answer.text))
            logger.error(answer)
        return res


class Zbx2Tg(object):

    isInited = False

    def __init__(self, debug=False):
        global logger
        #
        log_file = "{0}/{1}.log".format(zbxtg_settings.zbxtg_log_dir, zbxtg_settings.zbxtg_keyword)
        logging.basicConfig(level=(logging.INFO,logging.DEBUG)[debug])
        self.toDebug = debug
        logger = logging.getLogger("Zbx2Tg")
        # create file handler which logs even debug messages
        # fh = logging.FileHandler(log_file)
        fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5, encoding=None, delay=0)
        fh.setLevel((logging.INFO,logging.DEBUG)[debug])
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.debug("Starting Zbx2Tg script...")
        #
        self.isInited = True

    def Process(self,args):

        global logger
        global settings
        if not self.isInited: 
            return False

        settings_backup=copy.copy(settings)
        logger.debug("Process: {} ".format(args))
        logger.debug("ARGV, cnt={}".format(len(args)))
        for i,a in enumerate(args):
            logger.debug(" arg{} = {}".format(i,a))
        if len(args) < 4:
             print("Usage: zbxtg toID subject text")
             return False
        zbx_to = args[1]
        zbx_subject = args[2]
        zbx_text = args[3]
        #
        tg = TelegramAPI(zbxtg_settings.botAPIkey)
        res=tg.sendMessage(zbx_to,zbx_subject,zbx_text)
        settings=settings_backup
        return res

if __name__ == "__main__":
    debug=False
    if hasattr(zbxtg_settings,"debug"):
        debug=zbxtg_settings.debug
    if "--debug" in sys.argv:
        debug=True
    try: 
        zbx2tg = Zbx2Tg(debug)
        zbx2tg.Process(sys.argv)
    except Exception as inst:
        if logger: 
            logger.error(type(inst))
            logger.error(inst.args)
            logger.error(inst)
    finally:
        if logger: 
            logger.debug("Stopping Zbx2Tg script...")
