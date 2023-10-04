from elasticsearch import helpers
from elasticsearch.client import Elasticsearch
import socket, struct, ipaddress
import elasticsearch

import pandas as pd
import json

def isNaN(num):
    return num!=num


try:
    hosts = ["192.168.81.1", "192.168.81.2", "192.168.81.3","192.168.81.4", "192.168.81.5", "192.168.81.6"]
    port = 9200
    outputIndex = 'index_name'
    esIengine_Insert = Elasticsearch(hosts=hosts, port=port)
    esIengine_Insert.info()

    df = pd.read_csv('Sample.CSV', header=None)

    counter = 0
    batchSize = 10000
    eventCount = 1
    actions = []

    for index, row in df.iterrows():
        # print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        start_ip = socket.inet_ntoa(struct.pack('!L', row[0]))
        end_ip = socket.inet_ntoa(struct.pack('!L', row[1]))
        # print(start_ip)
        # print(end_ip)
        startip = ipaddress.IPv4Address(start_ip)
        endip = ipaddress.IPv4Address(end_ip)
        ipranges = [ipaddr for ipaddr in ipaddress.summarize_address_range(startip, endip)]
        # print(ipranges)
        isoCode = row[2]
        countryName = row[3]
        province = row[4]
        city = row[5]
        lat = row[6]
        lon = row[7]
        isp = row[8]

        for address in ipranges:
            if isNaN(isoCode):
                isoCode = ''
            if isNaN(isp):
                isp = ''
            if isNaN(city):
                city = ''
            if isNaN(province):
                province = ''
            if isNaN(countryName):
                countryName = ''
            doc = {
                "ipranges": str(address),
                "isocode": isoCode,
                "countryname": countryName,
                "province": province,
                "city": city,
                "latitude": lat,
                "longitude": lon,
                "isp": isp
            }

            doc2 = json.dumps(doc)

            action = {
                "_index" : outputIndex,
                "_type": "_doc",
                "_id": counter,
                "_source": doc2
            }
            actions.append(action)
            

            if len(actions) >= batchSize:
                helpers.bulk(esIengine_Insert,actions)
                del actions[0:len(actions)]
                counter += batchSize
                print(counter)
    if len(actions) > 0:
        helpers.bulk(esIengine_Insert,actions)
    print("ALL FINISHED")
            # esIengine_Insert.index(index="ip2loc", document=doc2)

except elasticsearch.ElasticsearchException as es1:
    print("Failed to insert record into ip2locations table ",es1)
