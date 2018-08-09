# zabbix-telegram

Lightweight Telegram Zabbix notifications script.

First idea comes from 
https://github.com/ableev/Zabbix-in-Telegram/
but script is fully rewritten/made simpler to meet own needs.

## Features
- [x] text/Markup/HTML modes
- [x] send to Telegram users or Group
- [x] send graphs from Zabbix to Telegram
- [x] fexible config - most parameters can be rewritten directly in message text

## Configuration / Installation

1. Install `requests` python module:</br>
   ```pip install requests```
2. Put next files in your `AlertScriptsPath` directory (you can find this path in your **zabbix_server.conf**, by default
  `/usr/lib/zabbix/alertscripts` ):
   * **zbxtg.py** - main script
   * **zbxtg_settings.py** - script settings
   * **zbxtg_test.py** - test script
   You can do it via console using commands:
   ```bash
   apt install python-pip
   wget https://raw.githubusercontent.com/BlackVS/zabbix-telegram/master/src/zbxtg.py
   chmod a+x zbxtg.py
   wget https://raw.githubusercontent.com/BlackVS/zabbix-telegram/master/src/zbxtg_settings.py
   wget https://raw.githubusercontent.com/BlackVS/zabbix-telegram/master/src/zbxtg_test.py
   ```
3. Create temp dir and allow Zabbix to write to it. By default temp directory is `/tmp/zbxtg` i.e.
```
mkdir /tmp/zbxtg
sudo chown zabbix:zabbix /tmp/zbxtg
```
4. Update `zbxtg_settings.py` with your settings (see below), at least:
   * bot API
   * unittests_targetID
   * zabbix_server
   * zabbix_api_user
   * zabbix_api_pass
 
 4. Add new media for Telegram in Zabbix web interface (see below)
 
### Settings
#### botAPIkey
To use notifications you must first create Telegram bot and get it's API key (token).
Check https://core.telegram.org/bots#6-botfather for details.

#### unittests_targetID
It is ID of user to get test results notifications.
Needed only if you wish to run tests.
To get your own ID in Telegram add **@MyTelegramID_bot** to your contacts in Telegram and send `/start` command to it
#### zabbix_server
URL of your Zabbix server in form `http::/server`
#### zabbix_api_user
From security reasons better to have separate read-only Zabbix user for accessing Zabbix API.
Just create read-only user (in my case named as **api**)
#### zabbix_api_pass
Password of read-only Zabbix user (i.e. **api** user)
#### zabbix_api_verify
**True** if you have proper valid certificates. In the case of self-signed ones make this parameter equal **False**
#### zbxtg_keyword
Don't change this parameter if not 100% sure %)
#### zbxtg_tmp_dir
Directory for temp files (for example, for graphs generated by Zabbix). Must have write permissions for Zabbix
#### zbxtg_log_dir
Log dir. Also must have write permissions for Zabbix.
#### debug
**True** if you wish get detailed log of running script.
#### msg_mode
None, "HTML", "Markdown" - which mode to use to format messages in Telegam. 
See:
https://core.telegram.org/bots/api#markdown-style 
https://core.telegram.org/bots/api#html-style. 
#### msg_subject_format_HTML
Default HTML mode formatting for message subject
#### msg_subject_format_Markdown
Default Markdown mode formatting for message subject
#### disable_web_page_preview
Default value for **disable_web_page_preview**
Disables link previews for links in this message
See https://core.telegram.org/bots/api#sendMessage
#### disable_notification
Default value for **disable_notification**
Sends the message silently. Users will receive a notification with no sound
See https://core.telegram.org/bots/api#sendMessage
#### graph_width
Default value for graph width
Can be modified in message templates
#### graph_height
Default value for graph height
Can be modified in message templates
#### graph_period
Default value for graph period
Can be modified in message templates

### Zabbix
1. Create separate media for Telegram.
In Zabbix: Administartion -> Media types -> Create media type :
![alt text](https://github.com/BlackVS/zabbix-telegram/raw/master/images/Zabbix-media.jpg "Media creation")
2. Add just created media to user which should receive Telegram notifications from Zabbix:
![alt text](https://github.com/BlackVS/zabbix-telegram/raw/master/images/Zabbix-media-user.jpg "Adding Media to user")
**Send to** - must contain numeric Telegram ID of user of group, not name!!!
To get ID of user use @MyTelegramID_bot
To get ID of group chat add @MyTelegramID_bot to this chat.
3. Add corresponding actions to generate new type notifications:
![alt text](https://github.com/BlackVS/zabbix-telegram/raw/master/images/Zabbix-actions-0.jpg "Custom actions - 0")
![alt text](https://github.com/BlackVS/zabbix-telegram/raw/master/images/Zabbix-actions-1.jpg "Custom actions - 1")
![alt text](https://github.com/BlackVS/zabbix-telegram/raw/master/images/Zabbix-actions-2.jpg "Custom actions - 2")
![alt text](https://github.com/BlackVS/zabbix-telegram/raw/master/images/Zabbix-actions-3.jpg "Custom actions - 3")
For convience default templates can be found here:
https://raw.githubusercontent.com/BlackVS/zabbix-telegram/master/src/zbxtg_message_templates.txt

### Message templates
#### Simple text
It can be just simple text with or without Zabbix macroses like standard e-mail notifications
You can add additional HTML (https://core.telegram.org/bots/api#html-style) or Markdown (https://core.telegram.org/bots/api#markdown-style ) formatting to these messages. In such case you must either change default **msg_mode** value in settings file or modify this value directly in message template in options section (see below)
#### Graphs
You can send graphs. For example:
```python
zbxtg:graph={
"title": "{HOST.HOST} - {TRIGGER.NAME}",
"itemid":{ITEM.ID1}
}
```
**zbxtg:graph** is graph section described by corresponded simple JSON format text.
**title** - title of graph
**itemid** - Zabbix item id for which graph is being generated (we use Zabbix {ITEM.ID1} to get it)
Also you can change default width, height, period, msg_mode values for graph.
For example:
```python
zbxtg:graph={
"title": "{HOST.HOST} - {TRIGGER.NAME}",
"itemid":{ITEM.ID1},
"width":1000,
"height":300,
"period":3600
}
```
Check https://raw.githubusercontent.com/BlackVS/zabbix-telegram/master/src/zbxtg_test.py for possible use cases.
#### Mixed content
You can mix both simple text and grapths in one template - in such case complex message will be split in set of simpler ones.
#### Options
You can add options section to modify some default values for each message template.
For example:
```python
zbxtg:options={ "msg_mode": "HTML", 
"disable_web_page_preview": false,
"disable_notification": false,
"width":600, 
"height":100, 
"period":10800, 
"debug": true
}
```
Order of applying values (from lowest to highest):
1. First default options from **zbxtg_settings.py** file applyed.
2. Next command line options applyed (if exists, for example --debug key).
3. zbxtg:options applyed next
4. For each graph zbxtg:graph options applyed.
I.e. if some option present in all 4 places for some graph - option from zbxtg:graph value will be used only.

### Debug
* You can use the following command to test script from command line: </br>
`./zbxtg.py "tg_userID" "message_subject" "message_body" --debug`
* Tests are dependant of concrete server i.e. they must be adjusted before run in your envirinment
---

### Known issues

#### 

