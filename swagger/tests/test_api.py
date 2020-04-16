import sys
sys.path.append('/api/client/')
import pytest
import time                                                                                                            
import openapi_client
from openapi_client import Configuration as configuration                                                                                                 
from openapi_client.rest import ApiException                                                                           
from pprint import pprint 
from openapi_client import  InlineResponse2002 as response
import time

oapiclient = openapi_client
configuration = oapiclient.Configuration("http://127.0.0.1:8080/practice/1.0.0")
api_client = openapi_client.ApiClient(configuration)
api_instance = openapi_client.DefaultApi(api_client)

time.sleep(5)


def test_uname_str():
    result = api_instance.uname_get()
    myresult = response.to_dict(result)
    if not isinstance(myresult['uname'], str):
        pytest.fail("Uname is not a string")       

def test_uptime_str():
    result = api_instance.uptime_get()
    myresult = response.to_dict(result)
    if not isinstance(myresult['uptime'], str):
        pytest.fail("Uptime is not a string")       

def test_cpu_cores():
    result = api_instance.cpu_get()
    myresult = response.to_dict(result)
    if not isinstance(myresult['cpu_cores'], int):
        pytest.fail("cpu_cores is not an int")

def test_cpu_mhz():
    result = api_instance.cpu_get()
    myresult = response.to_dict(result)
    if not isinstance(myresult['cpu_mhz'], float):
        pytest.fail("cpu_mhz is not a float")

def test_cpu_model():
    result = api_instance.cpu_get()
    myresult = response.to_dict(result)
    if not isinstance(myresult['cpu_model'], str):
        pytest.fail("cpu_model is not a string")

def test_date():
    result = api_instance.date_get()
    myresult = response.to_dict(result)
    if not isinstance(myresult['date'], str):
        pytest.fail("Date is not a string")

def test_memory():
    result = api_instance.memory_get()
    myresult = response.to_dict(result)

    if not isinstance(myresult['total_memory'], int):
        pytest.fail("Total memory is not an int")

    if not isinstance(myresult['available_memory'], int):
        pytest.fail("Available memory is not an int")

    if not isinstance(myresult['free_memory'], int):
        pytest.fail("Free memory is not an int")

def test_df():
    result = api_instance.df_get()
    myresult = response.to_dict(result)

    if not isinstance(myresult['device'], str):
        pytest.fail("Device is not a string")

    if not isinstance(myresult['space_used'], int):
        pytest.fail("Space used is not an int")

    if not isinstance(myresult['space_available'], int):
        pytest.fail("Space available is not an int")

    if not isinstance(myresult['percent_used'], str):
        pytest.fail("Percent used is not a string")


