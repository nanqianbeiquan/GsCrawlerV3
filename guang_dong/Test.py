# coding=utf-8

import codecs
import bs4
import json

import requests

f = codecs.open('/Users/likai/Documents/c.txt', 'r', 'utf-8')
for line in f:
    mc = json.loads(line)['inputCompanyName']
    # if mc == u'深圳大奥信息工程有限公司':
    #     print line
    if 'Registered_Info' in json.loads(line):
        mc = json.loads(line)['Registered_Info'][0]['Registered_Info:enterprisename']
        if mc == u'广州对外经济发展总公司':
            print '->', line
    # print "'"+mc+"',"
f.close()