import pytest
from kbtest.k60i.gui import Gui as gui
from kbtest.configuration.configuration import Configuration as config
import pprint

""" Tests for the Status page """

conf = config()

def notest_device_model():
    """ Verify the device model matches an expected value """
    system  = gui()
    system.login(ip=conf.system_ip, password=conf.system_password)
    result = system.status.get_device_info()
    if conf.system_model != result['model']:
        pytest.fail("Exepected model K60i not found on status page")
    
def notest_ethernet_mac():
    """ Verify the displayed mac address matches an expected value """
    system  = gui()
    system.login(ip=conf.system_ip, password=conf.system_password)
    result = system.status.get_device_info()
    if conf.system_mac != result['mac']:
        pytest.fail("Exepected mac not found on status page")

def notest_hardware_version():
    """ Verify the displayed hardware version matches an expected value """
    system  = gui()
    system.login(ip=conf.system_ip, password=conf.system_password)
    result = system.status.get_device_info()
    if int(conf.system_hardware_version) != int(result['hwrev']):
        pytest.fail("Exepected hardware version found on status page")        

def test_ssid():
    """ Verify the displayed ssid matches an expected value """
    system  = gui()
    system.login(ip=conf.system_ip, password=conf.system_password)
    result = system.status.get_wireless_info()
    if result['SSID'] != conf.system_ssid:
        pytest.fail("SSID did not match expeced value")

