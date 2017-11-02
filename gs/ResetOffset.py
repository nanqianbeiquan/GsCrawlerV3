from KafkaAPI import KafkaAPI


# prov_code_list = [10, 11, 12, 13, 14, 15, 21, 22, 23, 31, 32, 33, 34, 35, 36, 37, 41,
#                   42, 43, 44, 45, 46, 50, 51, 52, 53, 54, 61, 62, 63, 64, 65]

prov_code_list = [11]
group = 'Crawler'
for code in prov_code_list:
    topic_name = 'GsSrc%d' % code
    print topic_name
    kafka = KafkaAPI(topic_name)
    kafka.init_consumer(group)
    kafka.reset_offset()

