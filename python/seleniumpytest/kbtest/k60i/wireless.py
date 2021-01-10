import enum
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import pprint

class Wireless:
    """ This is the wireless page"""

    def __init__(self, parent):
        self.parent = parent

    # TODO: needto complete connection control table, link bump, link lock
    # TODO : id KB-C6-05-9C.bump <- for link bump  
    # TODO : id KB-C6-05-DC.unlock <- for unlock

    class DeviceRole(enum.Enum):
        Remote = 'wireless.wlan0.role0'
        Hub = 'wireless.wlan0.role1'
        RootHub = 'wireless.wlan0.role2'

    class CenterFrequency(enum.Enum):
        Freq_58320 = 'wireless.wlan0.center_freq_mhz0'
        Freq_60480 = 'wireless.wlan0.center_freq_mhz1'
        Freq_62640 = 'wireless.wlan0.center_freq_mhz1'


    def get_connection_control(self):
        """ Get the data from the connection control table"""
        self._navigate_to_page()
        # wait for this ajax table to load
        wait = WebDriverWait(self.parent.wd, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'fa-unlink')))
        # for good measure
        time.sleep(1)

        element = self.parent.wd.find_element_by_id('ccwireless-0-rpeers')
        tds = element.find_elements_by_tag_name('td')
        i = 0
        ddict={}
        store=[]
        for td in tds:
            if i == 3:
                ddict.update({store[0]:{store[1], store[2]}})
                store=[]
                i = 0
            if td.text:
                store.append(td.text)
                i+=1
        return ddict

    def get_device_role(self):
        """ Get the device's role """
        self._navigate_to_page()
        roles = [
            self.DeviceRole.Remote,
            self.DeviceRole.Hub,
            self.DeviceRole.RootHub,
        ]
        for role in roles:
            element = self.parent.wd.find_element_by_id(role.value)
            if element.is_selected():
                return role

    def set_device_role(self, deviceRole: DeviceRole):
        """ Set the device role """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id(deviceRole.value)
        self.parent.wd.execute_script("arguments[0].click();", element)

    def get_ssid(self):
        """ Get the device's SSID """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('wireless.wlan0.ssid')
        return element.get_attribute('value')

    def set_ssid(self, ssid=''):
        """ Set the SSID """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('wireless.wlan0.ssid')
        element.clear()
        element.send_keys(ssid)

    def get_airlink_encryption_passcode(self):
        """ Get the airlink passcode """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('wireless.wlan0.passcode')
        return element.get_attribute('value')

    def set_airlink_encryption_passcode(self, passCode=''):
        """ Set the airlink passcode """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('wireless.wlan0.passcode')
        element.clear()
        element.send_keys(passCode)

    def get_center_frequency(self):
        """ Get the center frequency """
        self._navigate_to_page()
        freqs = [
            self.CenterFrequency.Freq_58320,
            self.CenterFrequency.Freq_60480,
            self.CenterFrequency.Freq_62640
        ]
        for freq in freqs:
            element = self.parent.wd.find_element_by_id(freq.value)
            if element.is_selected():
                return freq

    def set_center_frequency(self, centerFrequency: CenterFrequency):
        """ Set the center frequency """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id(centerFrequency.value)
        self.parent.wd.execute_script("arguments[0].click();", element)

    def get_preferred_hub(self):
        """ Get the preferred hub """
        self._navigate_to_page()
        # TODO : if the role is not remote ... need to fail or error
        element = self.parent.wd.find_element_by_id('wireless.wlan0.preferred_hub')
        return element.get_attribute('value')

    def set_preferred_hub(self, preferredHub=''):
        """ Set the preferred hub """
        self._navigate_to_page()
        # TODO : if the role is not remote ... need to fail or error
        element = self.parent.wd.find_element_by_id('wireless.wlan0.preferred_hub')
        element.clear()
        element.send_keys(preferredHub)

    def _navigate_to_page(self):
        """ Go to the wireless page """
        if self.parent.wd.current_url != self.parent.baseurl + '/#wireless':
            element = self.parent.wd.find_element_by_id('wireless-tab')
            element.click()

      
