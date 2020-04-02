import time
import pprint

class Admin:
    """ This is the admin page"""

    def __init__(self, parent):
        self.parent = parent
        self.baseurl = self.parent.baseurl + "#/admin"

    def reboot(self):
        """ Reboot device """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('ctrl-reboot')
        element.click()
        elements = self.parent.wd.find_elements_by_tag_name('button')
        for element in elements:
            if 'Reboot' in element.text:
                try:
                    element.click()
                except:
                    pass    

    def locate_unit(self, timeout=0):     
        """
        Enable locate unit.
        
        Args:
            timeout (int, optional): how long to keep the LED on. Defaults to 0.
        """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('ctrl-locate-unit')
        element.click()
        time.sleep(1)
        element = self.parent.wd.find_element_by_tag_name('h5')
        if "Press OK to stop unit locate" in element.text:
            print("found dialog text")

        time.sleep(timeout)
        elements = self.parent.wd.find_elements_by_tag_name('button')
        for element in elements:
            if "OK" in element.text:
                element.click()

    def save_changes(self):
        """
        This is the save changes button.
        """        
        self._navigate_to_page() 
        element = self.parent.wd.find_element_by_id('cfg-submit-admin')
        element.click()

    def get_link_state_led(self):    
        """
        Get the status of the link state LED.
        
        Returns:
            boolean: True/False ... is the light enabled.
        """        
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('system.device.led_enable0')
        if element.is_selected():
            return True
        else: 
            return False  

    def enable_link_state_led(self, save=True):
        """
        Enalbe the link state LED.
        
        Args:
            save (bool, optional): Whether or not to save changes. Defaults to True.
        """        
        self._navigate_to_page() 
        if not self.get_link_state_led():
            element = self.parent.wd.find_element_by_id('system.device.led_enable0')
            self.parent.wd.execute_script("arguments[0].click();", element)
            if save:
                self.save_changes()
                if not self.get_link_state_led():
                    print("This is a problem")

    def disable_link_state_led(self, save=True):
        """ Disable the link state LED """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('system.device.led_enable0')
        if element.is_selected():
            self.parent.wd.execute_script("arguments[0].click();", element)
            if save:
                self.save_changes()
                if self.get_link_state_led():
                    print("This is a problem")

    def upgrade_firmware(self, file=False, tftp=False, filePath='', tftp_ip=''):
        """ Upgrade System Firmware"""
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('ctrl-upgrade-fw')
        element.click()
        time.sleep(2)
        elements = self.parent.wd.find_elements_by_tag_name('a')
        for element in elements:

            if "Upload File" in  element.text and file:
                element.click()
                element = self.parent.wd.find_element_by_id('localFwFile')
                element.clear()
                element.send_keys(filePath)

            if "Remote File" in  element.text and tftp:
                # do a tftp file
                element.click()
                element = self.parent.wd.find_element_by_id('tftpServer')
                element.clear()
                element.send_keys(tftp_ip)
                time.sleep(2)
                elements2 = self.parent.wd.find_elements_by_tag_name('button')
                for element2 in elements2:
                    if "Check for Newer Firmware" in element2.text:
                        element2.click()

        elements = self.parent.wd.find_elements_by_tag_name('button')
        for element in elements:
            if "Upgrade Firmware" in element.text:
                #element.click()
                time.sleep(30)

    def change_password(self, password):
        """ Change the user's password """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('ctrl-change-pass')
        element.click()

        element = self.parent.wd.find_element_by_id('password1')
        element.clear()
        element.send_keys(password)

        element = self.parent.wd.find_element_by_id('password2')
        element.clear()
        element.send_keys(password)

        element = self.parent.wd.find_element_by_id('changePassButton')
        element.click()

    def get_location(self):
        """ Get the value of the location field """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('system.bitclick.location')
        return element.get_attribute('value')

    def set_location(self, location='', save=True):
        """ Set the system location field """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('system.bitclick.location')
        element.clear()
        element.send_keys(location)

        if save:
            self.save_changes()

            element = self.parent.wd.find_element_by_id('system.bitclick.location')
            if location not in element.get_attribute('value'):
                print("big trouble in river city")

    def get_description(self):
        """ Get the value of the description field """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('system.bitclick.description')
        return element.get_attribute('value')


    def set_description(self, location='', save=True):
        """ Set the system description field """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('system.bitclick.description')
        element.clear()
        element.send_keys(location)

        if save:
            self.save_changes()

            element = self.parent.wd.find_element_by_id('system.bitclick.description')
            if location not in element.get_attribute('value'):
                print("big trouble in river city")

    def restore_defaults(self, save=True):
        """ restore the location, description and link state to their defaults """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('cfg-restore-admin')
        element.click()

        if save:
            self.save_changes()

            element = self.parent.wd.find_element_by_id('system.bitclick.description')
            if "system description not set" not in element.get_attribute('value'):
                print("big trouble in river city")

            element = self.parent.wd.find_element_by_id('system.bitclick.location')
            if "system location not set" not in element.get_attribute('value'):
                print("big trouble in river city")

            element = self.parent.wd.find_element_by_id('system.device.led_enabled0')
            if not element.is_selected():
                print("big trouble in river city")

    def get_login_alert(self):
        """ This is the alert dialog when a user tries to log in with an invalid password """
        alert = self.parent.wd.switch_to.alert
        text = alert.text
        alert.accept()
        return text
        

    def _navigate_to_page(self):
        """ Go to the admin page """
        if self.parent.wd.current_url != self.parent.baseurl + '/#admin':
            element = self.parent.wd.find_element_by_id('admin-tab')
            element.click()
