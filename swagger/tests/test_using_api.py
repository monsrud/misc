#from __future__ import print_function                                                                                 
import sys
sys.path.append('/api/client/') 
import time                                                                                                            
import openapi_client
from openapi_client import Configuration as configuration                                                                                                 
from openapi_client.rest import ApiException                                                                           
from pprint import pprint                                                                                              
                                                                                                                       

c = openapi_client
configuration = c.Configuration("http://127.0.0.1:8080/practice/1.0.0")
api_client = openapi_client.ApiClient(configuration)

api_instance = openapi_client.DefaultApi(api_client)

#no
#result = api_instance.date_get()
#pprint(result)

# no
result = api_instance.uname_get()
pprint(result)

# no
#result = api_instance.uptime_get()
#pprint(result)


# works
#result = api_instance.cpu_get()
#pprint(result)


# no
#result = api_instance.df_get()
#pprint(result)

# no
#result = api_instance.memory_get()
#pprint(result)


                                                                                                                       
# Defining host is optional and default to http://127.0.0.1:8080/monitor/1.0.0                                         
#configuration.host = "http://127.0.0.1:8080/monitor/1.0.0"                                                             
# Enter a context with an instance of the API client                                                                   
#with openapi_client.ApiClient(configuration.host) as api_client:                                                            
#    # Create an instance of the API class                                                                              
#    api_instance = openapi_client.DefaultApi(api_client)                                                               
#                                                                                                                       
#    try:                                                                                                               
#        # Get the cpu information for the system                                                                       
#        api_response = api_instance.cpu_get()                                                                          
#        pprint(api_response)                                                                                           
#    except ApiException as e:                                                                                          
#        print("Exception when calling DefaultApi->cpu_get: %s\n" % e)            
