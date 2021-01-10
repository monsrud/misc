
import enum

class Management:
    """ This is the management page"""

    def __init__(self, parent):
        self.parent = parent

    class IPAssignmentMethod(enum.Enum):
        Static = 'network.mgmt.proto0'
        Dynamic = 'network.mgmt.proto1'
        Auto = 'network.mgmt.proto3'

    # TODO: need to add get methods for  ipaddress, netmask, gateway, vlan id


    def get_ip_assignment_method(self):   

        """        
        Get the IP address assignment method
        """             
        
        self._navigate_to_page()
        atypes = [
            self.IPAssignmentMethod.Auto,
            self.IPAssignmentMethod.Static,
            self.IPAssignmentMethod.Dynamic
        ]

        for atype in atypes:
            element = self.parent.wd.find_element_by_id(atype.value)
            if element.is_selected():
                return atype

    def set_ip_assignment_method(self, ipAssignmentMethod: IPAssignmentMethod):
        """ Set mgmt interface to static, dynamic or auto """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id(ipAssignmentMethod.value)
        self.parent.wd.execute_script("arguments[0].click();", element)

    def set_ip_address(self, ipAddr=''):
        """ Set ip address """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('network.mgmt.ipaddr')
        element.clear()
        element.send_keys(ipAddr)

    def set_network_mask(self, subnetMask=''):
        """ Set subnet mask """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('network.mgmt.netmask')
        element.clear()
        element.send_keys(subnetMask)

    def set_network_gateway(self, gateway=''):
        """ Set network gateway """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('network.mgmt.gateway')
        element.clear()
        element.send_keys(gateway)

    def set_vlan_enable(self):
        """ Set VLAN enable """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('network.mgmt.vlan0')
        if not element.is_selected():
            self.parent.wd.execute_script("arguments[0].click();", element)

    def set_vlan_disable(self):
        """ Set VLAN disable """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('network.mgmt.vlan0')
        if element.is_selected():
            self.parent.wd.execute_script("arguments[0].click();", element)

    def set_vlan_id(self, vlanID=''):
        """ Set VLAN ID """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('network.mgmt.vid')
        element.clear()
        element.send_keys(vlanID)

    def save_changes(self):
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('cfg-submit-mgmtif')
        element.click()

    def discard_changes(self):
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('cfg-revert-mgmtif')
        element.click()

    def restore_defaults(self, save=True):
        """ restore the location, description and link state to their defaults """
        self._navigate_to_page()
        element = self.parent.wd.find_element_by_id('cfg-restore-mgmtif')
        element.click()
        # TODO: need to verify defaults are restored

    def _navigate_to_page(self):
        """ Go to the status page """
        if self.parent.wd.current_url != self.parent.baseurl + '/#mgmtif':
            element = self.parent.wd.find_element_by_id('mgmtif-tab')
            element.click()
