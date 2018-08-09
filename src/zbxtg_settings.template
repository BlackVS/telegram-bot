#################################################################################
# Set only in this values optionss

# Telegram related settings
# Please put here your own values!!!!
botAPIkey = "XXXXXXX:YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"  # telegram bot api key
unittests_targetID = '123456789'

# Zabbix related settings
# Please Zabbix administrator to create read-only Zabbix user.  
zabbix_server = "http://server"  # zabbix server full url
zabbix_api_user = "api"          # zabbix read-only user login
zabbix_api_pass = "pa$$w0rd"     # zabbix read-only user password
zabbix_api_verify = False        # True - do not ignore self signed certificates
                                 # False - ignore

# Zabbix2Telegram related settings
zbxtg_keyword = "zbxtg"  # keyword, don't change if not sure
zbxtg_tmp_dir = "/tmp/" + zbxtg_keyword #script/zabbix must have write permissions to this folder
zbxtg_log_dir = "/var/log/zabbix/"      #script/zabbix must have write permissions to this folder


#################################################################################
# Options which can be modified via commandline
debug = False

#################################################################################
# Next options can be changed via zbxtg:options dynamicly for each notigication:

msg_mode = "HTML"  # None , "HTML" or "Markdown"
msg_subject_format_HTML = "<b>{0}</b>"
msg_subject_format_Markdown = "*{0}*"

disable_web_page_preview = False
disable_notification = False
graph_width  = 1000
graph_height = 200
graph_period = 8*60*60
