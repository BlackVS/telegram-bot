#!/usr/bin/env python
# coding: utf-8
import unittest
import zbxtg_settings
import zbxtg
import sys

getfname = lambda n=0: "Calling test: {}".format(sys._getframe(n + 1).f_code.co_name)
to = zbxtg_settings.unittests_targetID
#itemid=1348
itemid=2071

class TestStringMethods(unittest.TestCase):

    #def test_textOnly(self):
    #    zbx2tg = zbxtg.Zbx2Tg(True)
    #    self.assertTrue(zbx2tg.Process([
    #                    __file__, 
    #                    to, 
    #                    getfname(), 
    #                    'It is test message, Please ignore it', 
    #                    '--debug'])
    #                    )

    def test_graphOnly1(self):
        zbx2tg = zbxtg.Zbx2Tg(True)
        self.assertTrue(zbx2tg.Process([
                        __file__, 
                        to, 
                        getfname(), 
                        'zbxtg:options={ "msg_mode": "HTML", \
                                         "disable_web_page_preview": false,\
                                         "disable_notification": false,\
                                         "debug": true\
                                        }\
                         zbxtg:graph={  "title": "Test graph #1 - graph: 400x100 1 day", \
                                        "width":400, \
                                        "height":100, \
                                        "period":600, \
                                        "itemid": %s \
                                        }' % (itemid)
                       ])
                      )

    #def test_graphOnly2(self):
    #    zbx2tg = zbxtg.Zbx2Tg(True)
    #    self.assertTrue(zbx2tg.Process([
    #                    __file__, 
    #                    to, 
    #                    getfname(), 
    #                    'zbxtg:options={ "msg_mode": "HTML", \
    #                                     "disable_web_page_preview": false,\
    #                                     "disable_notification": false,\
    #                                     "width":600, \
    #                                     "height":100, \
    #                                     "period":10800, \
    #                                     "debug": true\
    #                                    }\
    #                     zbxtg:graph={  "title": "Test graph #2 - options : 600x100 3 days", \
    #                                    "itemid":%s \
    #                                    }' % (itemid)
    #                   ])
    #                  )

    #def test_graphOnly3(self):
    #    zbx2tg = zbxtg.Zbx2Tg(True)
    #    self.assertTrue(zbx2tg.Process([
    #                    __file__, 
    #                    to, 
    #                    getfname(), 
    #                    'zbxtg:options={ "msg_mode": "HTML", \
    #                                     "disable_web_page_preview": false,\
    #                                     "disable_notification": false,\
    #                                     "debug": true\
    #                                    }\
    #                     zbxtg:graph={  "title": "Test graph #3 - default", \
    #                                    "msg_mode": "Markdown",\
    #                                    "itemid":%s \
    #                                    }' % (itemid)
    #                   ])
    #                  )

    #def test_mixedContent(self):
    #    zbx2tg = zbxtg.Zbx2Tg(False)
    #    self.assertTrue(zbx2tg.Process([
    #                    __file__, 
    #                    to, 
    #                    getfname(), 
    #                    'Prefix text\n\rzbxtg:graph={"title":"XXX service is online","width":400,"height":100,"period":10800,"itemid":%s}\n\rEnd text' % itemid, 
    #                    '--debug'
    #                    ])
    #                    )

if __name__ == '__main__':
    unittest.main()
