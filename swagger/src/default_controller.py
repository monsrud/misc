import subprocess
import json
from flask import jsonify

def df_get():
    output =  subprocess.check_output(['df'], shell=True)
    output = output.decode('utf-8')
    space_used = None
    space_available = None
    percent_used = None
    result = None
    for line in output.split('\n'):
        if 'overlay' in line:
            line = line.replace('\n','')
            parts = line.split()
            result = {'device': parts[0], 
                  'space_used': int(parts[2]),
                  'space_available': int(parts[3]),
                  'percent_used': parts[4]
            }      
            break

    return jsonify(result)

def uptime_get():
    uptime = None
    output =  subprocess.check_output(['uptime'], shell=True)
    output = output.decode('utf-8')
    output = output.replace('\n','')
    parts = output.split()
    uptime = parts[2]
    uptime = uptime.replace(',','')
    result = {'uptime': uptime} 
    return jsonify(result)

def date_get():
    date = None
    output =  subprocess.check_output(['date'], shell=True)
    output = output.decode('utf-8')
    date = output.replace('\n','')
    result = {'date': date}
    return jsonify(result)

def uname_get():
    uname = None
    output =  subprocess.check_output(['uname -a'], shell=True)
    output = output.decode('utf-8')
    uname = output.replace('\n','')
    result = {'uname': uname}
    return jsonify(result)

def cpu_get():
    cpu_model = None
    cpu_mhz = None
    cpu_cores = None
    output =  subprocess.check_output(['cat','/proc/cpuinfo'])
    output = output.decode('utf-8')
    for line in output.split('\n'):
        line = line.replace('\n','')
        parts = line.split(":")
        line = ''.join(line.split())
        if len(parts) >=1:
            if "model name" in parts[0]:
                cpu_model = parts[1].strip()
            if "cpu MHz" in parts[0]:
                cpu_mhz = parts[1].strip()
            if "cpu cores" in parts[0]:
                cpu_cores = parts[1].strip()
    result = {
        'cpu_mhz': cpu_mhz,
        'cpu_cores': cpu_cores,
        'cpu_model': cpu_model
    }
    #return result
    #return json.dumps(result)
    return jsonify(result)

def memory_get():
    total_memory = None
    available_memory = None
    free_memory = None
    output =  subprocess.check_output(['cat','/proc/meminfo'])
    output = output.decode('utf-8')
    for line in output.split('\n'):
        line = line.replace('\n','')
        parts = line.split()
        if len(parts) >= 1:
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
    #return result
    #return json.dumps(result)
    return jsonify(result)




   
    



