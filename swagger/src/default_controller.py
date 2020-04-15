#import connexion
#import six
#from openapi_server.models.inline_response200 import InlineResponse200  # noqa: E501
#from openapi_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
#from openapi_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
#from openapi_server import util

import os
import json

def df_get():
    stream = os.popen('df / | tail -1')
    output = stream.read()
    parts = output.split()
    result = {'device': parts[0], 
          'space_used': parts[2],
          'space_available': parts[3],
          'percent_used': parts[4]
        }      
    return json.dumps(result)

def uptime_get():
    stream = os.popen('uptime')
    output = stream.read()
    parts = output.split()
    uptime = parts[2]
    uptime = uptime.replace(',','')
    result = {'uptime': uptime} 
    return json.dumps(result)

def date_get():
    stream = os.popen('date')
    output = stream.read()
    output = output.replace('\n','')
    return json.dumps({'date': output})

def uname_get():
    stream = os.popen('uname -a')
    output = stream.read()
    output = output.replace('\n','')
    return json.dumps({'uname': output})

def cpu_get():
    cpu_model = None
    cpu_mhz = None
    cpu_cores = None
    stream = os.popen('cat /proc/cpuinfo')
    output = stream.readlines()
    for line in output:
        line = line.replace('\n','')
        parts = line.split(":")
        line = ''.join(line.split())
        #line = re.sub(' +', '', line)
        if "model name" in parts[0]:
            cpu_model = parts[1]
        if "cpu MHz" in parts[0]:
            cpu_mhz = parts[1]
        if "cpu cores" in parts[0]:
            cpu_cores = parts[1]
    result = {
        'cpu_mhz': cpu_mhz,
        'cpu_cores': cpu_cores,
        'cpu_model': cpu_model
    }
    return result



def memory_get():
    total_memory = None
    available_memory = None
    free_memory = None
    stream = os.popen('cat /proc/meminfo')
    output = stream.readlines()
    for line in output:
        line = line.replace('\n','')
        parts = line.split()      
        if "MemTotal" in parts[0]:
            total_memory = parts[1]
        if "MemFree" in parts[0]:
            free_memory = parts[1]
        if "MemAvailable" in parts[0]:
            available_memory = parts[1]  
    result = {
        'total_memory': total_memory,
        'free_memory': free_memory,
        'available_memory': available_memory
    }
    return json.dumps(result)





    
    


  
