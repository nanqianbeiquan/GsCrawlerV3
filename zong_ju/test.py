# coding=utf-8

import requests

# x = "124.135.116.205:8213"
# proxy = {'http': x, 'https': x}
#
# r = requests.get('http://118.190.114.196:8888/get-node-list', proxies=proxy)
# print r.text

r = requests.get('http://www.gsxt.gov.cn/%7B6OSxphvVmVDlCtLm6fb7FP3KrCIAwnVSsInpRooxijcTifhiruGhfdF2YsSWiejYftLCnoAWCzyKql-HBbKFkMfjhg0tZpL9H7ycDA9fif7UJPDjPheqsGhIh9KCUI-S0_VV_k5sfy9g_SWoCbgnOQ-1495186483410%7D',allow_redirects=False)
r.encoding = 'utf-8'
print r.status_code
