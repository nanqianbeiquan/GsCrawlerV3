# coding=utf-8

import requests

# headers = {"User-Agent":  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
#                         "Host": "sh.gsxt.gov.cn",
#                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                         "Accept-Encoding": "gzip, deflate",
#                         "Cache-Control": "max-age=0",
#                         "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
#                         "Connection": "keep-alive",
#                         # "Referer": "http://sh.gsxt.gov.cn/notice/search/ent_info_list",
#                         }
# url ='http://sh.gsxt.gov.cn/notice/notice/view_investor?uuid=sfq7DEHqT49f.aBhv0IrOA=='
# # url = 'http://sh.gsxt.gov.cn/notice/notice/view_investor?uuid=A33vd9m7QY9f.aBhv0IrOA==&wscckey=9620311f67da5c3e_1488857832'
# r = requests.get(url, headers=headers, verify=False)
# print r.headers
# print "*"*20
# print r.cookies
# print "*"*20
# r.encoding ='utf8'
# print r.text.encode('utf8')

import requests
url = 'http://sh.gsxt.gov.cn/notice/notice/view_investor'
headers = { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0' }
data = { 'uuid':'gCgBiy.BYeNf.aBhv0IrOA==' , 'wscckey':'0b59d07fc7c71f9d_1488865230' }
r= requests.post(url,data=data,headers=headers,timeout=5)
r.encoding='utf8'
print r.text