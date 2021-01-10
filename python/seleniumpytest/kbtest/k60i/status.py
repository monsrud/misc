
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pprint 
import time

class Status:
    """ This is the status page"""

    def __init__(self, parent):
        self.parent = parent

    def get_header_info(self):
        """ Get the informaton in the page header """

        self._navigate_to_page()

        hostname = self.parent.wd.find_element_by_id('header-hostname')
        description = self.parent.wd.find_element_by_id('header-desc')
        user_description = self.parent.wd.find_element_by_id('header-user-descr')
        user = self.parent.wd.find_element_by_id('header-user')
        location = self.parent.wd.find_element_by_id('header-location')

        return {
            'hostname': hostname.text,
            'description': description.text,
            'user_description': user_description.text,
            'user': user.text,
            'location': location.text
        }

    def get_device_info(self):
        """ Get device information from the table on the Status page """

        self._navigate_to_page()

        model = self.parent.wd.find_element_by_id('dinfo-model')
        mac = self.parent.wd.find_element_by_id('dinfo-emac')
        hwrev = self.parent.wd.find_element_by_id('dinfo-hwrev')
        swver = self.parent.wd.find_element_by_id('dinfo-swver')
        blver = self.parent.wd.find_element_by_id('dinfo-blver')
        time = self.parent.wd.find_element_by_id('dinfo-time')

        return {
            'model':model.text,
            'mac':mac.text,
            'hwrev':hwrev.text,
            'swver':swver.text,
            'blver':blver.text,
            'time':time.text
        }

    def get_management_info(self):
        """ Get management information from the status tab """

        self._navigate_to_page()

        mgmtip = self.parent.wd.find_element_by_id('dinfo-mgmtip')
        mgmtmask = self.parent.wd.find_element_by_id('dinfo-mgmtmask')
        mgmtgw = self.parent.wd.find_element_by_id('dinfo-mgmtgw')
        return {
            'mgmtip': mgmtip.text,
            'mgmtmask': mgmtmask.text,
            'mgmtgw': mgmtgw.text
        }

    def get_lan_info(self):
        """ Get the LAN information from the status tab """

        self._navigate_to_page()

        lan1enable = self.parent.wd.find_element_by_id('lanst-1-enable')
        lan2enable = self.parent.wd.find_element_by_id('lanst-2-enable')
        lan3enable = self.parent.wd.find_element_by_id('lanst-3-enable')

        lan1link = self.parent.wd.find_element_by_id('lanst-1-link')
        lan2link = self.parent.wd.find_element_by_id('lanst-2-link')
        lan3link = self.parent.wd.find_element_by_id('lanst-3-link')

        lan1duplex = self.parent.wd.find_element_by_id('lanst-1-duplex')
        lan2duplex = self.parent.wd.find_element_by_id('lanst-2-duplex')
        lan3duplex = self.parent.wd.find_element_by_id('lanst-3-duplex')

        lan1speed = self.parent.wd.find_element_by_id('lanst-1-speed')
        lan2speed = self.parent.wd.find_element_by_id('lanst-2-speed')
        lan3speed = self.parent.wd.find_element_by_id('lanst-3-speed')

        lan1max = self.parent.wd.find_element_by_id('lanst-1-max')
        lan2max = self.parent.wd.find_element_by_id('lanst-2-max')
        lan3max = self.parent.wd.find_element_by_id('lanst-3-max')

        lan1poetype = self.parent.wd.find_element_by_id('lanst-1-poetype')
        lan2poetype = self.parent.wd.find_element_by_id('lanst-2-poetype')
        lan3poetype = self.parent.wd.find_element_by_id('lanst-3-poetype')

        lan1peers = self.parent.wd.find_element_by_id('lanst-1-peers')
        lan2peers = self.parent.wd.find_element_by_id('lanst-2-peers')
        lan3peers = self.parent.wd.find_element_by_id('lanst-3-peers')

        return {

               'lan1': {
                   'enable':lan1enable.text,
                   'link':lan1link.text,
                   'duplex': lan1duplex.text,
                   'speed':lan1speed.text,
                   'max':lan1max.text,
                   'poetype':lan1poetype.text,
                   'peers':lan1peers.text
                   },

               'lan2': {
                   'enable':lan2enable.text,
                   'link':lan2link.text,
                   'duplex': lan2duplex.text,
                   'speed':lan2speed.text,
                   'max':lan2max.text,
                   'poetype':lan2poetype.text,
                   'peers':lan2peers.text
                   },

               'lan3': {
                   'enable':lan3enable.text,
                   'link':lan3link.text,
                   'duplex': lan3duplex.text,
                   'speed':lan3speed.text,
                   'max':lan3max.text,
                   'poetype':lan3poetype.text,
                   'peers':lan3peers.text
                   }
        }

    def get_wireless_info(self):
        """ Get Wireless informaton from the Status tab """
        self._navigate_to_page()

        frequency = self.parent.wd.find_element_by_id('dinfo-0-freq')
        ssid = self.parent.wd.find_element_by_id('dinfo-0-ssid')
        role = self.parent.wd.find_element_by_id('dinfo-0-role')
        peers = self.parent.wd.find_element_by_id('dinfo-0-rpeers')

        mypeers = []
        for peer in peers.text.split("\n"):
            if "Peer Name" in peer:
                continue
            parts = peer.split(' ')
            connect_time = ' '.join(parts[2:len(parts)])
            mypeers.append({'PeerName': parts[0], 'SignalQuality': parts[1], 'ConnectTime': connect_time})

        return {
            'Frequency': frequency.text,
            'SSID': ssid.text,
            'Role': role.text,
            'Peers': mypeers
        }

    def _navigate_to_page(self):
        """ Go to the status page """
        if self.parent.wd.current_url != self.parent.baseurl + '/#status':
            element = self.parent.wd.find_element_by_id('status-tab')
            element.click()
            # wait for one of the last elements on the page to load
            for i in range(1,10):
                element = WebDriverWait(self.parent.wd, 5).until(EC.presence_of_element_located((By.ID, 'dinfo-mgmtgw')))
                if element.text and i:
                    break
                time.sleep(1)      


