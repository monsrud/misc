import os
import pytest
import yaml
import pprint

class Configuration:

    """ 
    Configuration facts for a K60
    """

    system_ip = None
    system_mask = None
    system_username = None
    system_password = None
    system_model = None
    system_hardware_version = None
    system_firmware_version = None
    system_boot_loader_version = None
    system_unit_name = None
    system_radio_peers = None
    system_location = None
    system_description = None
    system_ssid = None
    system_role = None
    system_mac = None


    def __init__(self, system_ip=None):

        if system_ip:
            self.system_ip = system_ip

        if os.environ.get('K60'):
            self.system_ip =   os.environ.get('K60')  

            if os.path.exists(self.system_ip + ".yaml"):
                with open(self.system_ip + ".yaml", 'r') as f:
                    self.config = yaml.load(f)
            else:
                pytest.fail("No yaml configuration file found")

            if 'system_ip' not in self.config:
               pytest.fail("system_ip must be specified in configuration", allow_module_level=True)    
  
        self.system_mask = self.config['system_mask']
        self.system_gateway = self.config['system_gateway']
        self.system_username = self.config['system_username']
        self.system_password = self.config['system_password']
        self.system_model = self.config['system_model']
        self.system_hardware_version = self.config['system_hardware_version']
        self.system_firmware_version = self.config['system_firmware_version']
        self.system_boot_loader_version = self.config['system_boot_loader_version']
        self.system_unit_name = self.config['system_unit_name']
        self.system_radio_peers = self.config['system_radio_peers']
        self.system_location = self.config['system_location']
        self.system_description = self.config['system_description']
        self.system_ssid = self.config['system_ssid']
        self.system_role = self.config['system_role']
        self.system_mac = self.config['system_mac']


                
