import pytest
from kbtest.k60i.gui import Gui as gui
from kbtest.configuration.configuration import Configuration as config


""" The environment varialbe K60 must be set to the IP of the system under test"""

conf = config()

def test_invalid_login():
    """ Try to log into the GUI with an incorrect password """
    system  = gui()
    system.login(ip=conf.system_ip, password='foober')
    result = system.admin.get_login_alert()
    if not "Authorization Failure" in result:
        pytest.fail("Error attempting to login with incorrect password")

def test_valid_login():
    """ Log into the GUI """    
    system  = gui()
    system.login(ip=conf.system_ip, password=conf.system_password)    
    result = system.wd.find_element_by_id('ctrl-reboot')
    if not result:
        pytest.fail("Failed to log into GUI")
