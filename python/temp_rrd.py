#!/usr/bin/python3

import requests
import os
import rrdtool
import time
import urllib3
from pprint import pprint

urllib3.disable_warnings()
radio_ip_addresses = ['10.80.0.75']

ts = time.time()

def create_rrd(rrd_name):
    if not os.path.isfile(rrd_name):
        rrdtool.create(rrd_name, '--step', '60',
            'DS:value:GAUGE:300:-50:150',
            'RRA:AVERAGE:0.5:5:7d',
            'RRA:MAX:0.5:5:7d',
            'RRA:MIN:0.5:5:7d'
        )

def update_rrd(rrd_name, value):
    rrdtool.update(rrd_name,'N:%s' %(value))

def create_daily_graph(rrd_name, graph_title, value_title):

    rrdtool.graph(
        graph_title + '1day.png',
        '--end', "now",
        '--start',"end-86400s",
        '-t', "%s" % (graph_title),
        '--imgformat','PNG',
        "DEF:value=%s:value:AVERAGE" %(rrd_name),
        "LINE1:value#FF0000:{}".format(value_title),
        "GPRINT:value:AVERAGE:Avg %2.0lf %s",
        "GPRINT:value:MIN:Min %2.0lf %s",
        "GPRINT:value:MAX:Max %2.0lf %s"
    )

def create_weekly_graph(rrd_name, graph_title, value_title):

    rrdtool.graph(
        graph_title + '7day.png',
        '--end', "now",
        '--start',"end-604800s",
        '-t', "%s" % (graph_title),
        '--imgformat','PNG',
        "DEF:value=%s:value:AVERAGE" %(rrd_name),
        "LINE1:value#FF0000:{}".format(value_title),
        "GPRINT:value:AVERAGE:Avg %2.0lf %s",
        "GPRINT:value:MIN:Min %2.0lf %s",
        "GPRINT:value:MAX:Max %2.0lf %s"
    )


for radio_ip_address in radio_ip_addresses:    
    
    response = requests.get('https://' + radio_ip_address + '/rest/v001/device/device_status', verify=False)
    json = response.json()
    processor_temperature = float(json.get('temperature_processor'))

    response = requests.get('https://' + radio_ip_address + '/rest/v001/device/node_identity', verify=False)
    json = response.json()
    kbname = json.get('name')
       
    rrd_name = kbname + '_processortemp.rrd'

    create_rrd(rrd_name)
    update_rrd(rrd_name,processor_temperature)
    create_daily_graph(rrd_name, "{} Processor Temperature".format(kbname),'Temp')
    create_weekly_graph(rrd_name, "{} Processor Temperature".format(kbname),'Temp')
