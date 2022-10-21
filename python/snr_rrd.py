#!/usr/bin/python3

import requests
import os
import rrdtool
import time
import urllib3
urllib3.disable_warnings()

# Make RRD graphs signal to noise statistics for wireless radios


radio_ip_addresses = ['10.100.2.40','10.100.2.37','10.100.2.39','10.100.2.41']

ts = time.time()

for radio_ip_address in radio_ip_addresses:    
    
    response = requests.get('https://' + radio_ip_address + '/rest/v002/device/radio_status', verify=False)
    json = response.json()
       
    radio = json['radio']
    
    for r in radio:
    
        interface_name = r['name']
        kb_name = json['kb_name']
    
        links = r['links']
    
        for l in links:
    
            downlink_ssnr = None
            uplink_ssnr = None
            link_name = None
            
            if l.get('is_alive') == True:
                
                downlink_ssnr =  l['downlink'].get('phystatus.ssnrEst')
                uplink_ssnr =  l['uplink'].get('phystatus.ssnrEst')
                link_name = l.get('link_name')
    
                ts = time.time()
                
                rrd_name = json['kb_name'] + '_' + link_name + '_SSNR' + '.rrd'
                rrd_name = rrd_name.replace(':','-')
                link_name = link_name.replace(':','-')
                
                # create database if it doesn't exist
                if not os.path.isfile(rrd_name):
                    rrdtool.create(rrd_name, '--step', '60',
                        'DS:uplink_ssnr:GAUGE:300:0:40',
                        'DS:downlink_ssnr:GAUGE:300:0:40',
                        'RRA:AVERAGE:0.5:5:7d', 
                        'RRA:MAX:0.5:5:7d', 
                        'RRA:MIN:0.5:5:7d' 
                    )
           
                rrdtool.update(rrd_name,'N:%s:%s' %(uplink_ssnr,downlink_ssnr))
                
                graph_name = json['kb_name'] + '_' + link_name + '.png'
                graph_title = kb_name + " " + link_name
                graph_name = graph_name.replace(':','-')
                rrdtool.graph(
                    graph_name,
                    '-t', "%s %s" % (kb_name,link_name),
                    '--imgformat','PNG',
                    "DEF:up=%s:uplink_ssnr:AVERAGE" %(rrd_name),
                    "DEF:down=%s:downlink_ssnr:AVERAGE" %(rrd_name),
                    "LINE1:up#FF0000:UP",
                    "LINE2:down#00FF00:DOWN",
                    "GPRINT:up:AVERAGE:Avg Up %2.0lf %s",
                    "GPRINT:down:AVERAGE:Avg Down %2.0lf %s",
                    "GPRINT:up:MIN:Min Up %2.0lf %s",
                    "GPRINT:down:MIN:Min Down %2.0lf %s",
                    "GPRINT:up:MAX:Max Up %2.0lf %s",
                    "GPRINT:down:MAX:Max Down %2.0lf %s"
                )

