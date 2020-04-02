from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time


from . import admin
from . import status
from . import management
from . import wireless
from socket import gethostname
import time
from datetime import datetime

class Gui:
    baseurl = ""
    wd = None

    def __init__(self):
        self.admin = admin.Admin(self)
        self.management = management.Management(self)
        self.status = status.Status(self)
        self.wireless = wireless.Wireless(self)
        self.baseurl = ''
        self.wd = None


    def login(self, ip=None, password=None):
        self.baseurl = "https://" + ip

        options = Options()
        options.set_capability("acceptInsecureCerts", True)
        options.accept_untrusted_certs = True
        options.add_argument('--ignore-certificate-errors')
        if "systest-dev1" == gethostname():
            options.headless = True
        now = datetime.now()
        now = now.strftime("%d-%b-%Y-%H:%M:%S.%f")
        self.wd = webdriver.Chrome(options=options,
                                   service_args=["--verbose", 
                                   "--log-path=/tmp/" + now + " chromedriver.log"])
        self.wd.set_window_size(1366,758)
        self.wd.implicitly_wait(10)
        time.sleep(1)
        url = self.baseurl + "#/admin"
        self.wd.get(url)
        element = self.wd.find_element_by_id("admin-tab")
        element.click()

        time.sleep(1)

        element = self.wd.find_element_by_id("passwordInput")
        element.clear()
        element.send_keys(password)

        time.sleep(1)
        element = self.wd.find_element_by_id("passEnter")
        self.wd.execute_script("document.getElementById('passEnter').click()")
        # not so fast...
        time.sleep(2)

        
