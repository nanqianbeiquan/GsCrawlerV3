# coding=utf-8

from codecs import open

f = open(r'/Users/likai/Documents/data/fact_registered_info/000000_0', 'r', 'utf-8')
# line = f.readline().split('\001')
for line in f:
    print '|'.join(line.split('\001'))
