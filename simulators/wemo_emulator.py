#!/usr/bin/env python
# requires python3
import email.utils
import requests
import select
import socket
import struct
import sys
import time
import urllib
import uuid
import pprint
import time
import re
import http.client
import random
from random import randint
from time import sleep
from netifaces import AF_INET
import netifaces
import getopt
import sys
import os
import optparse
import subprocess
import psutil
import string

"""
This script can be used to emulate a Wemo outlet plug. I used a real outlet plug, Wireshark, and a LAN tap to
watch SSDP traffic over the network. Then wrote this script to simulate these devices.
This allowed us to test our system without actually having to have the Wemo device present. 
Admittedly, it is not great code but functional.
"""

if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

parser = optparse.OptionParser()
parser.add_option('--address', dest='address', help='IP Address', type="string")
parser.add_option('--type', dest='devicetype', choices=['motion','mini','insight','plug'],
default='mini', help='motion|mini|insight|plug')
parser.add_option('--debug', dest='debug', action='store_true', default=False, help='Debug Logging')

(options, args) = parser.parse_args()

if options.address is None:
    print("You must specify an IP address for your wemo device to use")
    sys.exit(1)

DEBUG = False
if options.debug == True:
    DEBUG = True

DEBUG_SSDP = False 


if options.devicetype == "plug":
    DEVICE_TYPE = "F7C027"  # WeMo Smart Switch
elif options.devicetype == "motion":
    DEVICE_TYPE = "F7C028"  # WeMo Motion Sensor
elif options.devicetype == "mini":
    DEVICE_TYPE = "F7C063"  # WeMo Mini
elif options.devicetype == "insight":
    DEVICE_TYPE = "F7029V2"  # WeMo Insight
elif options.devicetype is None:
    print ("You must specify a device type of switch|motion|mini|insight")
    sys.exit(1)
else:
    print ("Unsupported WeMo type specified")
    sys.exit(1)

print(options.address)
print(type(options.address))

interface_ip = options.address


octets = interface_ip.split('.')
print(len(octets))
if len(octets) != 4:
    print("Invalid IP")
    sys.exit(1)

switch_name = "wemo_" + str(octets[3])


try:
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['ip', 'link', 'set', switch_name, 'down'], stdout=devnull, stderr=devnull)
except(subprocess.CalledProcessError):
    pass

try:
    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['ip', 'link', 'delete', switch_name], stdout=devnull, stderr=devnull)
except(subprocess.CalledProcessError):
    pass


with open(os.devnull, 'wb') as devnull:
    ret = subprocess.check_call(['ip', 'link', 'add', 'link', 'eth0', switch_name,
                                 'type', 'macvlan'], stdout=devnull, stderr=devnull)


with open(os.devnull, 'wb') as devnull:
    ret = subprocess.check_call(['ifconfig', switch_name, interface_ip, 'netmask',
                                 '255.255.255.0'], stdout=devnull, stderr=devnull)


#
# Wemo Motion F7C028
#
F7C028_SETUP_XML = """<?xml version="1.0"?>
<root xmlns="urn:Belkin:device-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <device>
<deviceType>urn:Belkin:device:sensor:1</deviceType>
<friendlyName>%(device_name)s (Motion)</friendlyName>
    <manufacturer>Belkin International Inc.</manufacturer>
    <manufacturerURL>http://www.belkin.com</manufacturerURL>
    <modelDescription>Belkin Plugin Socket 1.0</modelDescription>
    <modelName>Socket</modelName>
    <modelNumber>1.0</modelNumber>
    <modelURL>http://www.belkin.com/plugin/</modelURL>
<serialNumber>%(device_serial)s</serialNumber>
<UDN>uuid:Sensor-1_0-%(device_serial)s</UDN>
    <UPC>123456789</UPC>
<macAddress>08863B6C1338</macAddress>
<firmwareVersion>WeMo_US_2.00.4494.PVT</firmwareVersion>
<iconVersion>1|49153</iconVersion>
<binaryState>0</binaryState>
    <iconList> 
      <icon> 
        <mimetype>jpg</mimetype> 
        <width>100</width> 
        <height>100</height> 
        <depth>100</depth> 
         <url>icon.jpg</url> 
      </icon> 
    </iconList>
    <serviceList>
      <service>
        <serviceType>urn:Belkin:service:WiFiSetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:WiFiSetup1</serviceId>
        <controlURL>/upnp/control/WiFiSetup1</controlURL>
        <eventSubURL>/upnp/event/WiFiSetup1</eventSubURL>
        <SCPDURL>/setupservice.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:timesync:1</serviceType>
        <serviceId>urn:Belkin:serviceId:timesync1</serviceId>
        <controlURL>/upnp/control/timesync1</controlURL>
        <eventSubURL>/upnp/event/timesync1</eventSubURL>
        <SCPDURL>/timesyncservice.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:basicevent:1</serviceType>
        <serviceId>urn:Belkin:serviceId:basicevent1</serviceId>
        <controlURL>/upnp/control/basicevent1</controlURL>
        <eventSubURL>/upnp/event/basicevent1</eventSubURL>
        <SCPDURL>/eventservice.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:firmwareupdate:1</serviceType>
        <serviceId>urn:Belkin:serviceId:firmwareupdate1</serviceId>
        <controlURL>/upnp/control/firmwareupdate1</controlURL>
        <eventSubURL>/upnp/event/firmwareupdate1</eventSubURL>
        <SCPDURL>/firmwareupdate.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:rules:1</serviceType>
        <serviceId>urn:Belkin:serviceId:rules1</serviceId>
        <controlURL>/upnp/control/rules1</controlURL>
        <eventSubURL>/upnp/event/rules1</eventSubURL>
        <SCPDURL>/rulesservice.xml</SCPDURL>
      </service>
	  
      <service>
        <serviceType>urn:Belkin:service:metainfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:metainfo1</serviceId>
        <controlURL>/upnp/control/metainfo1</controlURL>
        <eventSubURL>/upnp/event/metainfo1</eventSubURL>
        <SCPDURL>/metainfoservice.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:remoteaccess:1</serviceType>
        <serviceId>urn:Belkin:serviceId:remoteaccess1</serviceId>
        <controlURL>/upnp/control/remoteaccess1</controlURL>
        <eventSubURL>/upnp/event/remoteaccess1</eventSubURL>
        <SCPDURL>/remoteaccess.xml</SCPDURL>
      </service>
	   
      <service>
        <serviceType>urn:Belkin:service:deviceinfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:deviceinfo1</serviceId>
        <controlURL>/upnp/control/deviceinfo1</controlURL>
        <eventSubURL>/upnp/event/deviceinfo1</eventSubURL>
        <SCPDURL>/deviceinfoservice.xml</SCPDURL>
      </service>
	   
      <service>
        <serviceType>urn:Belkin:service:smartsetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:smartsetup1</serviceId>
        <controlURL>/upnp/control/smartsetup1</controlURL>
        <eventSubURL>/upnp/event/smartsetup1</eventSubURL>
        <SCPDURL>/smartsetup.xml</SCPDURL>
      </service>


    </serviceList>
   <presentationURL>/pluginpres.html</presentationURL>
</device>
</root>
"""

#
# WeMo F7029V2 (Insight)
#
F7029V2_SETUP_XML = """<?xml version="1.0"?>
<root xmlns="urn:Belkin:device-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <device>
<deviceType>urn:Belkin:device:insight:1</deviceType>
<friendlyName>%(device_name)s (Insight)</friendlyName>
    <manufacturer>Belkin International Inc.</manufacturer>
    <manufacturerURL>http://www.belkin.com</manufacturerURL>
    <modelDescription>Belkin Insight 1.0</modelDescription>
    <modelName>Insight</modelName>
    <modelNumber>1.0</modelNumber>
    <modelURL>http://www.belkin.com/plugin/</modelURL>
<serialNumber>%(device_serial)s</serialNumber>
<UDN>uuid:Insight-1_0-%(device_serial)s</UDN>
    <UPC>123456789</UPC>
<macAddress>94103ECF7394</macAddress>
<firmwareVersion>WeMo_WW_2.00.10966.PVT-OWRT-InsightV2</firmwareVersion>
<iconVersion>1|49153</iconVersion>
<binaryState>0</binaryState>
    <iconList> 
      <icon> 
        <mimetype>jpg</mimetype> 
        <width>100</width> 
        <height>100</height> 
        <depth>100</depth> 
         <url>icon.jpg</url> 
      </icon> 
    </iconList>
    <serviceList>
      <service>
        <serviceType>urn:Belkin:service:WiFiSetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:WiFiSetup1</serviceId>
        <controlURL>/upnp/control/WiFiSetup1</controlURL>
        <eventSubURL>/upnp/event/WiFiSetup1</eventSubURL>
        <SCPDURL>/setupservice.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:timesync:1</serviceType>
        <serviceId>urn:Belkin:serviceId:timesync1</serviceId>
        <controlURL>/upnp/control/timesync1</controlURL>
        <eventSubURL>/upnp/event/timesync1</eventSubURL>
        <SCPDURL>/timesyncservice.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:basicevent:1</serviceType>
        <serviceId>urn:Belkin:serviceId:basicevent1</serviceId>
        <controlURL>/upnp/control/basicevent1</controlURL>
        <eventSubURL>/upnp/event/basicevent1</eventSubURL>
        <SCPDURL>/eventservice.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:firmwareupdate:1</serviceType>
        <serviceId>urn:Belkin:serviceId:firmwareupdate1</serviceId>
        <controlURL>/upnp/control/firmwareupdate1</controlURL>
        <eventSubURL>/upnp/event/firmwareupdate1</eventSubURL>
        <SCPDURL>/firmwareupdate.xml</SCPDURL>
      </service>
      <service>
        <serviceType>urn:Belkin:service:rules:1</serviceType>
        <serviceId>urn:Belkin:serviceId:rules1</serviceId>
        <controlURL>/upnp/control/rules1</controlURL>
        <eventSubURL>/upnp/event/rules1</eventSubURL>
        <SCPDURL>/rulesservice.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:metainfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:metainfo1</serviceId>
        <controlURL>/upnp/control/metainfo1</controlURL>
        <eventSubURL>/upnp/event/metainfo1</eventSubURL>
        <SCPDURL>/metainfoservice.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:remoteaccess:1</serviceType>
        <serviceId>urn:Belkin:serviceId:remoteaccess1</serviceId>
        <controlURL>/upnp/control/remoteaccess1</controlURL>
        <eventSubURL>/upnp/event/remoteaccess1</eventSubURL>
        <SCPDURL>/remoteaccess.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:deviceinfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:deviceinfo1</serviceId>
        <controlURL>/upnp/control/deviceinfo1</controlURL>
        <eventSubURL>/upnp/event/deviceinfo1</eventSubURL>
        <SCPDURL>/deviceinfoservice.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:insight:1</serviceType>
        <serviceId>urn:Belkin:serviceId:insight1</serviceId>
        <controlURL>/upnp/control/insight1</controlURL>
        <eventSubURL>/upnp/event/insight1</eventSubURL>
        <SCPDURL>/insightservice.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:smartsetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:smartsetup1</serviceId>
        <controlURL>/upnp/control/smartsetup1</controlURL>
        <eventSubURL>/upnp/event/smartsetup1</eventSubURL>
        <SCPDURL>/smartsetup.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:manufacture:1</serviceType>
        <serviceId>urn:Belkin:serviceId:manufacture1</serviceId>
        <controlURL>/upnp/control/manufacture1</controlURL>
        <eventSubURL>/upnp/event/manufacture1</eventSubURL>
        <SCPDURL>/manufacture.xml</SCPDURL>
      </service>

    </serviceList>
   <presentationURL>/pluginpres.html</presentationURL>
</device>
</root>
"""

#
# Wemo Mini F7C063
#
F7C063_SETUP_XML = """<?xml version="1.0"?>
<root xmlns="urn:Belkin:device-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <device>
<deviceType>urn:Belkin:device:controllee:1</deviceType>
<friendlyName>%(device_name)s (Mini)</friendlyName>
    <manufacturer>Belkin International Inc.</manufacturer>
    <manufacturerURL>http://www.belkin.com</manufacturerURL>
    <modelDescription>Belkin Plugin Socket 1.0</modelDescription>
<modelName>Socket</modelName>
    <modelNumber>1.0</modelNumber>
    <modelURL>http://www.belkin.com/plugin/</modelURL>
<serialNumber>%(device_serial)s</serialNumber>
<UDN>uuid:Socket-1_0-%(device_serial)s</UDN>
    <UPC>123456789</UPC>
<macAddress>6038E0F3161C</macAddress>
<firmwareVersion>WeMo_US_2.00.6395.PVT</firmwareVersion>
<iconVersion>2|49153</iconVersion>
<binaryState>%(state)s</binaryState>
    <iconList>
      <icon>
        <mimetype>jpg</mimetype>
        <width>100</width>
        <height>100</height>
        <depth>100</depth>
         <url>icon.jpg</url>
      </icon>
    </iconList>
    <serviceList>
      <service>
        <serviceType>urn:Belkin:service:WiFiSetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:WiFiSetup1</serviceId>
        <controlURL>/upnp/control/WiFiSetup1</controlURL>
        <eventSubURL>/upnp/event/WiFiSetup1</eventSubURL>
        <SCPDURL>/setupservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:timesync:1</serviceType>
        <serviceId>urn:Belkin:serviceId:timesync1</serviceId>
        <controlURL>/upnp/control/timesync1</controlURL>
        <eventSubURL>/upnp/event/timesync1</eventSubURL>
        <SCPDURL>/timesyncservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:basicevent:1</serviceType>
        <serviceId>urn:Belkin:serviceId:basicevent1</serviceId>
        <controlURL>/upnp/control/basicevent1</controlURL>
        <eventSubURL>/upnp/event/basicevent1</eventSubURL>
        <SCPDURL>/eventservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:firmwareupdate:1</serviceType>
        <serviceId>urn:Belkin:serviceId:firmwareupdate1</serviceId>
        <controlURL>/upnp/control/firmwareupdate1</controlURL>
        <eventSubURL>/upnp/event/firmwareupdate1</eventSubURL>
        <SCPDURL>/firmwareupdate.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:rules:1</serviceType>
        <serviceId>urn:Belkin:serviceId:rules1</serviceId>
        <controlURL>/upnp/control/rules1</controlURL>
        <eventSubURL>/upnp/event/rules1</eventSubURL>
        <SCPDURL>/rulesservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:metainfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:metainfo1</serviceId>
        <controlURL>/upnp/control/metainfo1</controlURL>
        <eventSubURL>/upnp/event/metainfo1</eventSubURL>
        <SCPDURL>/metainfoservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:remoteaccess:1</serviceType>
        <serviceId>urn:Belkin:serviceId:remoteaccess1</serviceId>
        <controlURL>/upnp/control/remoteaccess1</controlURL>
        <eventSubURL>/upnp/event/remoteaccess1</eventSubURL>
        <SCPDURL>/remoteaccess.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:deviceinfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:deviceinfo1</serviceId>
        <controlURL>/upnp/control/deviceinfo1</controlURL>
        <eventSubURL>/upnp/event/deviceinfo1</eventSubURL>
        <SCPDURL>/deviceinfoservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:smartsetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:smartsetup1</serviceId>
        <controlURL>/upnp/control/smartsetup1</controlURL>
        <eventSubURL>/upnp/event/smartsetup1</eventSubURL>
        <SCPDURL>/smartsetup.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:manufacture:1</serviceType>
        <serviceId>urn:Belkin:serviceId:manufacture1</serviceId>
        <controlURL>/upnp/control/manufacture1</controlURL>
        <eventSubURL>/upnp/event/manufacture1</eventSubURL>
        <SCPDURL>/manufacture.xml</SCPDURL>
      </service>
      
    </serviceList>
   <presentationURL>/pluginpres.html</presentationURL>
</device>
</root>
"""

#
# Wemo Smart Switch F7C027
#
F7C027_SETUP_XML = """<?xml version="1.0"?>
<root xmlns="urn:Belkin:device-1-0">
<specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <device>
    <deviceType>urn:Belkin:device:controllee:1</deviceType>
    <friendlyName>%(device_name)s (SmartSwitch)</friendlyName>
    <manufacturer>Belkin International Inc.</manufacturer>
    <modelName>Socket</modelName>
    <modelNumber>1.0</modelNumber>
    <UDN>uuid:Socket-1_0-%(device_serial)s</UDN>
    <serialNumber>%(device_serial)s</serialNumber>
    <macAddress>EC1A59763091</macAddress>
    <firmwareVersion>WeMo_US_2.00.6395.PVT</firmwareVersion>
    <iconVersion>1|49153</iconVersion>
    <binaryState>%(state)s</binaryState>
        <iconList> 
      <icon> 
        <mimetype>jpg</mimetype> 
        <width>100</width> 
        <height>100</height> 
        <depth>100</depth> 
         <url>icon.jpg</url> 
      </icon> 
    </iconList>
    <serviceList>
      <service>
        <serviceType>urn:Belkin:service:WiFiSetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:WiFiSetup1</serviceId>
        <controlURL>/upnp/control/WiFiSetup1</controlURL>
        <eventSubURL>/upnp/event/WiFiSetup1</eventSubURL>
        <SCPDURL>/setupservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:timesync:1</serviceType>
        <serviceId>urn:Belkin:serviceId:timesync1</serviceId>
        <controlURL>/upnp/control/timesync1</controlURL>
        <eventSubURL>/upnp/event/timesync1</eventSubURL>
        <SCPDURL>/timesyncservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:basicevent:1</serviceType>
        <serviceId>urn:Belkin:serviceId:basicevent1</serviceId>
        <controlURL>/upnp/control/basicevent1</controlURL>
        <eventSubURL>/upnp/event/basicevent1</eventSubURL>
        <SCPDURL>/eventservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:firmwareupdate:1</serviceType>
        <serviceId>urn:Belkin:serviceId:firmwareupdate1</serviceId>
        <controlURL>/upnp/control/firmwareupdate1</controlURL>
        <eventSubURL>/upnp/event/firmwareupdate1</eventSubURL>
        <SCPDURL>/firmwareupdate.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:rules:1</serviceType>
        <serviceId>urn:Belkin:serviceId:rules1</serviceId>
        <controlURL>/upnp/control/rules1</controlURL>
        <eventSubURL>/upnp/event/rules1</eventSubURL>
        <SCPDURL>/rulesservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:metainfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:metainfo1</serviceId>
        <controlURL>/upnp/control/metainfo1</controlURL>
        <eventSubURL>/upnp/event/metainfo1</eventSubURL>
        <SCPDURL>/metainfoservice.xml</SCPDURL>
      </service>

      <service>
        <serviceType>urn:Belkin:service:remoteaccess:1</serviceType>
        <serviceId>urn:Belkin:serviceId:remoteaccess1</serviceId>
        <controlURL>/upnp/control/remoteaccess1</controlURL>
        <eventSubURL>/upnp/event/remoteaccess1</eventSubURL>
        <SCPDURL>/remoteaccess.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:deviceinfo:1</serviceType>
        <serviceId>urn:Belkin:serviceId:deviceinfo1</serviceId>
        <controlURL>/upnp/control/deviceinfo1</controlURL>
        <eventSubURL>/upnp/event/deviceinfo1</eventSubURL>
        <SCPDURL>/deviceinfoservice.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:smartsetup:1</serviceType>
        <serviceId>urn:Belkin:serviceId:smartsetup1</serviceId>
        <controlURL>/upnp/control/smartsetup1</controlURL>
        <eventSubURL>/upnp/event/smartsetup1</eventSubURL>
        <SCPDURL>/smartsetup.xml</SCPDURL>
      </service>
      
      <service>
        <serviceType>urn:Belkin:service:manufacture:1</serviceType>
        <serviceId>urn:Belkin:serviceId:manufacture1</serviceId>
        <controlURL>/upnp/control/manufacture1</controlURL>
        <eventSubURL>/upnp/event/manufacture1</eventSubURL>
        <SCPDURL>/manufacture.xml</SCPDURL>
      </service>

    </serviceList>
   <presentationURL>/pluginpres.html</presentationURL>
    
  </device>
</root>
"""




def dbg(msg):
    global DEBUG
    if DEBUG:
        print(msg)
        sys.stdout.flush()

def dbg_SSDP(msg):
    global DEBUG_SSDP
    if DEBUG_SSDP:
        print(msg)
        sys.stdout.flush()


def get_interface_for_ip(ip_address):
    for iface in netifaces.interfaces():
        if 'wemo' in iface:
            ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            if (ip == ip_address):
                return iface

# A simple utility class to wait for incoming data to be
# ready on a socket.
class poller:
    def __init__(self):
        if 'poll' in dir(select):
            self.use_poll = True
            self.poller = select.poll()
        else:
            self.use_poll = False
        self.targets = {}

    def add(self, target, fileno = None):
        if not fileno:
            fileno = target.fileno()
        if self.use_poll:
            self.poller.register(fileno, select.POLLIN)
        self.targets[fileno] = target

    def remove(self, target, fileno = None):
        if not fileno:
            fileno = target.fileno()
        if self.use_poll:
            self.poller.unregister(fileno)
        del(self.targets[fileno])

    def poll(self, timeout=0):
        if self.use_poll:
            ready = self.poller.poll(timeout)
        else:
            ready = []
            if len(self.targets) > 0:
                (rlist, wlist, xlist) = select.select(self.targets.keys(), [], [], timeout)
                ready = [(x, None) for x in rlist]
        for one_ready in ready:
            target = self.targets.get(one_ready[0], None)
            if target:
                target.do_read(one_ready[0])
 

# Base class for a generic UPnP device. This is far from complete
class upnp_device(object):
    this_host_ip = interface_ip

    def __init__(self, listener, poller, port, root_url, server_version, persistent_uuid, serial_number):
        self.listener = listener
        self.poller = poller
        self.port = port
        self.root_url = root_url
        self.server_version = server_version
        self.persistent_uuid = persistent_uuid
        self.serial_number = serial_number
        self.uuid = uuid.uuid4()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip_address, self.port))
        self.socket.listen(5)
        if self.port == 0:
            self.port = self.socket.getsockname()[1]
        self.poller.add(self)
        self.client_sockets = {}
        self.listener.add_device(self)

    def fileno(self):
        return self.socket.fileno()

    def do_read(self, fileno):
        if fileno == self.socket.fileno():
            (client_socket, client_address) = self.socket.accept()
            self.poller.add(self, client_socket.fileno())
            self.client_sockets[client_socket.fileno()] = client_socket
        else:
            data, sender = self.client_sockets[fileno].recvfrom(4096)
            if not data:
                self.poller.remove(self, fileno)
                del(self.client_sockets[fileno])
            else:
                data = data.decode('utf-8')
                self.handle_request(data, sender, self.client_sockets[fileno])

    def handle_request(self, data, sender, socket):
        pass

    def get_name(self):
        return "unknown"
        
    def respond_to_search(self, destination):
        dbg_SSDP("Responding to search for %s" % self.get_name())
        date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        location_url = self.root_url % {'ip_address': self.ip_address, 'port': self.port}

        if DEVICE_TYPE == "F7C027" or DEVICE_TYPE == "F7C063":
            tag = "uuid:Socket-1_0-" + self.serial_number + "::urn:Belkin:device:controllee:1"
            message = ("HTTP/1.1 200 OK\r\n"
                  "CACHE-CONTROL: max-age=86400\r\n"
                  "DATE: %s\r\n"
                  "EXT:\r\n"
                  "LOCATION: %s\r\n"
                  "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
                  "01-NLS: %s\r\n"
                  "SERVER: %s\r\n"
                  "X-User-Agent: redsonic\r\n"
                  "ST: urn:Belkin:device:controllee:1\r\n"
                  "USN: %s\r\n" % (date_str, location_url, self.persistent_uuid, self.server_version, tag))
            message += "\r\n"
            self.sender_socket.sendto(message.encode('utf-8'), destination)

        if DEVICE_TYPE == "F7029V2":
            dbg("This is a wemo insight")

            tag = "uuid:Insight-1_0-" + self.serial_number + "::urn:Belkin:device:insight:1"
            message = ("HTTP/1.1 200 OK\r\n"
                       "CACHE-CONTROL: max-age=86400\r\n"
                       "DATE: %s\r\n"
                       "LOCATION: %s\r\n"
                       "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
                       "01-NLS: %s\r\n"
                       "SERVER: %s\r\n"
                       "X-User-Agent: redsonic\r\n"
                       "ST: urn:Belkin:device:insight:1\r\n"
                       "USN: %s\r\n" % (date_str, location_url, self.persistent_uuid, self.server_version, tag))
            message += "\r\n"
            self.sender_socket.sendto(message.encode('utf-8'), destination)

        if DEVICE_TYPE == "F7C028":
            dbg("This is a wemo motion sensor")

            tag = "uuid:Sensor-1_0-" + self.serial_number + "::urn:Belkin:device:sensor:1"
            message = ("HTTP/1.1 200 OK\r\n"
                       "CACHE-CONTROL: max-age=86400\r\n"
                       "DATE: %s\r\n"
                       "LOCATION: %s\r\n"
                       "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
                       "01-NLS: %s\r\n"
                       "SERVER: %s\r\n"
                       "X-User-Agent: redsonic\r\n"
                       "ST: urn:Belkin:device:sensor:1\r\n"
                       "USN: %s\r\n" % (date_str, location_url, self.persistent_uuid, self.server_version, tag))
            message += "\r\n"
            self.sender_socket.sendto(message.encode('utf-8'), destination)


# This subclass does the bulk of the work to mimic a WeMo F7C063 switch on the network.
class wemo(upnp_device):
    # ( 1 = on, 0 = off).
    state = "0"
    callback_ip = ""
    callback_port = ""
    persistent_uuid = ""
    seq_number = 0

    @staticmethod
    def make_uuid():
        myuuid = uuid.uuid4()
        return str(myuuid)

    @staticmethod
    def make_serial_number():
        serial = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14))
        return serial

    def __init__(self, name, listener, poller, ip_address, port):
        self.serial_number = self.make_serial_number()
        self.name = name
        self.ip_address = ip_address
        persistent_uuid = self.make_uuid()
        self.sender_socket = listener.sender_socket

        upnp_device.__init__(self, listener, poller, port, "http://%(ip_address)s:%(port)s/setup.xml",
                             "Unspecified, UPnP/1.0, Unspecified", persistent_uuid, self.serial_number)
        dbg("FauxMo device '%s' ready on %s:%s" % (self.name, self.ip_address, self.port))

    def get_name(self):
        return self.name

    def getFreePort(self):
        begin = 10000
        end = 65535
        port = randint(begin, end)
        portsinuse = []
        while True:
            conns = psutil.net_connections()
            for conn in conns:
                portsinuse.append(conn.laddr[1])
            if port in portsinuse:
                port = randint(begin, end)
            else:
                break
        return port

    def notify(self, state):
        self.persistent_uuid
        self.seq_number = self.seq_number + 1

        body = """
        <e:propertyset xmlns:e="urn:schemas-upnp-org:event-1-0">
        <e:property>
        <BinaryState>%(state)s</BinaryState>
        </e:property>
        </e:propertyset>    
        """

        body = body % {'state': state}

        my_port = self.getFreePort()

        conn = http.client.HTTPConnection(self.callback_ip, self.callback_port, source_address=(self.ip_address,my_port))


        headers = {"Content-type": "text/xml; charset=utf-8",
                   "NT": "upnp:event",
                   "NTS": "upnp:propchange",
                   "SID": "uuid:" + self.persistent_uuid
                   }

        conn.request("NOTIFY", "/", body, headers)

        return True

    def handle_request(self, data, sender, socket):
        dbg(data)
        dbg(sender)

        if data.find('SUBSCRIB') == 0:
            dbg("THIS IS A SUBSCRIBE")

        if data.find('GET /setup.xml HTTP/1.1') == 0 and self.ip_address in data:
            dbg("Responding to setup.xml for %s" % self.name)

            # "F7C027"  # WeMo Smart Switch
            # "F7C063"  # WeMo Mini

            if DEVICE_TYPE == "F7C063":
                xml = F7C063_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}

            elif DEVICE_TYPE == "F7C027":
                xml = F7C027_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}
            elif DEVICE_TYPE == "F7029V2":
                xml = F7029V2_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}

            elif DEVICE_TYPE == "F7C028":
                xml = F7C028_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}

            date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
            message = ("HTTP/1.1 200 OK\r\n"
                       "CONTENT-LENGTH: %d\r\n"
                       "CONTENT-TYPE: text/xml\r\n"
                       "DATE: %s\r\n"
                       "LAST-MODIFIED: Sat, 01 Jan 2000 00:01:15 GMT\r\n"
                       "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                       "X-User-Agent: redsonic\r\n"
                       "CONNECTION: close\r\n"
                       "\r\n"
                       "%s" % (len(xml), date_str, xml))
            socket.send(message)

        elif data.find('SOAPAction: "urn:Belkin:service:basicevent:1#SetBinaryState"') != -1 and self.ip_address in data:

            if data.find('<BinaryState>1</BinaryState>') != -1:
                # on
                dbg("Responding to ON for %s" % self.name)
                self.notify(1)

            elif data.find('<BinaryState>0</BinaryState>') != -1:
                # off
                dbg("Responding to OFF for %s" % self.name)
                self.notify(0)
            else:
                dbg("Unknown Binary State request:")


# This subclass does the bulk of the work to mimic a WeMo F7C063 switch on the network.
class wemo(upnp_device):
    # ( 1 = on, 0 = off).
    state = "0"
    callback_ip = ""
    callback_port = ""
    persistent_uuid = ""
    seq_number = 0

    @staticmethod
    def make_uuid():
        myuuid = uuid.uuid4()
        return str(myuuid)

    @staticmethod
    def make_serial_number():
        serial = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14))
        return serial

    def __init__(self, name, listener, poller, ip_address, port):
        self.serial_number = self.make_serial_number()
        self.name = name
        self.ip_address = ip_address
        persistent_uuid = self.make_uuid()
        self.sender_socket = listener.sender_socket

        upnp_device.__init__(self, listener, poller, port, "http://%(ip_address)s:%(port)s/setup.xml",
                             "Unspecified, UPnP/1.0, Unspecified", persistent_uuid, self.serial_number)
        dbg("FauxMo device '%s' ready on %s:%s" % (self.name, self.ip_address, self.port))

    def get_name(self):
        return self.name

    def getFreePort(self):
        begin = 10000
        end = 65535
        port = randint(begin, end)
        portsinuse = []
        while True:
            conns = psutil.net_connections()
            for conn in conns:
                portsinuse.append(conn.laddr[1])
            if port in portsinuse:
                port = randint(begin, end)
            else:
                break
        return port

    def notify(self, state):
        self.persistent_uuid
        self.seq_number = self.seq_number + 1

        body = """
        <e:propertyset xmlns:e="urn:schemas-upnp-org:event-1-0">
        <e:property>
        <BinaryState>%(state)s</BinaryState>
        </e:property>
        </e:propertyset>    
        """

        body = body % {'state': state}

        my_port = self.getFreePort()

        conn = http.client.HTTPConnection(self.callback_ip, self.callback_port, source_address=(self.ip_address,my_port))

        headers = {"Content-type": "text/xml; charset=utf-8",
                   "NT": "upnp:event",
                   "NTS": "upnp:propchange",
                   "SID": "uuid:" + self.persistent_uuid
                   }

        conn.request("NOTIFY", "/", body, headers)

        return True

    def handle_request(self, data, sender, socket):
        dbg(data)
        dbg(sender)

        if data.find('SUBSCRIB') == 0:
            dbg("THIS IS A SUBSCRIBE")

        if data.find('GET /setup.xml HTTP/1.1') == 0 and self.ip_address in data:
            dbg("Responding to setup.xml for %s" % self.name)

            # "F7C027"  # WeMo Smart Switch
            # "F7C063"  # WeMo Mini

            if DEVICE_TYPE == "F7C063":
                xml = F7C063_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}

            elif DEVICE_TYPE == "F7C027":
                xml = F7C027_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}
            elif DEVICE_TYPE == "F7029V2":
                xml = F7029V2_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}
            elif DEVICE_TYPE == "F7C028":
                xml = F7C028_SETUP_XML % {'device_name': self.name,
                                          'device_serial': self.serial_number,
                                          'state': self.state}


            date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
            message = ("HTTP/1.1 200 OK\r\n"
                       "CONTENT-LENGTH: %d\r\n"
                       "CONTENT-TYPE: text/xml\r\n"
                       "DATE: %s\r\n"
                       "LAST-MODIFIED: Sat, 01 Jan 2000 00:01:15 GMT\r\n"
                       "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                       "X-User-Agent: redsonic\r\n"
                       "CONNECTION: close\r\n"
                       "\r\n"
                       "%s" % (len(xml), date_str, xml))
            socket.send(message.encode('utf-8'))



        elif data.find('SOAPAction: "urn:Belkin:service:basicevent:1#SetBinaryState"') != -1 and self.ip_address in data:
            success = False

            if data.find('<BinaryState>1</BinaryState>') != -1:
                # on
                dbg("Responding to ON for %s" % self.name)
                self.notify(1)
                success = True
            elif data.find('<BinaryState>0</BinaryState>') != -1:
                # off
                dbg("Responding to OFF for %s" % self.name)
                self.notify(0)
                success = True
            else:
                dbg("Unknown Binary State request:")

            if success:

                soap = """
                <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
                <u:SetBinaryStateResponse xmlns:u="urn:Belkin:service:basicevent:1">
                <BinaryState>%(state)s</BinaryState>
                </u:SetBinaryStateResponse>
                </s:Body> </s:Envelope>
                """
                soap = soap % {'state': self.state}



                date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
                message = ("HTTP/1.1 200 OK\r\n"
                           "CONTENT-LENGTH: %d\r\n"
                           "CONTENT-TYPE: text/xml; charset=\"utf-8\"\r\n"
                           "DATE: %s\r\n"
                           "EXT:\r\n"
                           "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                           "X-User-Agent: redsonic\r\n"
                           "CONNECTION: close\r\n"
                           "\r\n"
                           "%s" % (len(soap), date_str, soap))
                socket.send(message.encode('utf-8'))
            else:
                dbg("ERROR: SetBinaryState Not Successful")

        elif data.find('SOAPACTION: "urn:Belkin:service:timesync:1#TimeSync"') != -1 and self.ip_address in data:
            dbg("This is a time sync request")
            timenow = time.time

            soap = """
            <?xml version="1.0" encoding="utf-8"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
            <u:TimeSync xmlns:u="urn:Belkin:service:timesync:1">
            <UTC>%(time)s</UTC>
            <TimeZone>-05.00</TimeZone>
            <dst>1</dst>
            <DstSupported>1</DstSupported>
            </u:TimeSync>
            </s:Body>
            </s:Envelope>    
            """

            soap = soap % {'time': timenow}

            date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
            message = ("HTTP/1.1 200 OK\r\n"
                       "CONTENT-LENGTH: %d\r\n"
                       "CONTENT-TYPE: text/xml; charset=\"utf-8\"\r\n"
                       "DATE: %s\r\n"
                       "EXT:\r\n"
                       "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                       "X-User-Agent: redsonic\r\n"
                       "CONNECTION: close\r\n"
                       "\r\n"
                       "%s" % (len(soap), date_str, soap))
            socket.send(message.encode('utf-8'))

        elif data.find('SOAPACTION: "urn:Belkin:service:basicevent:1#GetBinaryState"') != -1 and self.ip_address in data:
            dbg("This is a get binary state request")

            soap = """
            <?xml version="1.0"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
            <u:GetBinaryStateResponse xmlns:u="urn:Belkin:service:basicevent:1">
            <BinaryState>%(state)s</BinaryState>
            </u:GetBinaryStateResponse>  
            </s:Body></s:Envelope>
            """

            soap = soap % {'state': self.state}

            date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
            message = ("HTTP/1.1 200 OK\r\n"
                       "CONTENT-LENGTH: %d\r\n"
                       "CONTENT-TYPE: text/xml; charset=\"utf-8\"\r\n"
                       "DATE: %s\r\n"
                       "EXT:\r\n"
                       "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                       "X-User-Agent: redsonic\r\n"
                       "CONNECTION: close\r\n"
                       "\r\n"
                       "%s" % (len(soap), date_str, soap))

            socket.send(message.encode('utf-8'))

        elif 'CALLBACK' in data and self.ip_address in data:
            dbg("This is a callback request")

            regexp = ".*<http://([0-9\.]+).*"

            data = data.replace('\n',' ')
            m = re.match(regexp, data)

            if m:
                self.callback_ip = m.group(1)
                self.callback_port = "39500"


                self.notify(self.state)
            else:
                dbg("Regexp not matched...")

        else:
            dbg("handle request dropped through to here")

class upnp_broadcast_responder(object):
    TIMEOUT = 0

    def __init__(self):
        #self.devices = []
        self.device = None
        self.sender_socket = None

    def init_socket(self):
        ok = True
        self.ip = '239.255.255.250'
        self.port = 1900
        try:
            #Set up server socket
            self.ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            dbg("FAILED TO SET UP SOCKET")
            ok = False

        try:
            self.ssock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,
                                  socket.inet_aton(self.ip)+socket.inet_aton(interface_ip))
        except Exception as e:
            dbg('WARNING: Failed to join multicast group:')
            ok = False


        try:
            self.ssock.bind((self.ip, self.port))
        except Exception as e:
            dbg("FAILED TO BIND")
            #print("WARNING: Failed to bind %s:%d: %s" , (self.ip,self.port,e))
            ok = False

        if ok:
            dbg("Listening for UPnP broadcasts")

        interface_name = get_interface_for_ip(interface_ip)
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sender_socket.setsockopt(socket.SOL_SOCKET, 25, interface_name.encode('utf-8'))
        if DEVICE_TYPE == "F7029V2" or DEVICE_TYPE == "F7C028":
            sender_socket.bind((interface_ip, 3076))
        self.sender_socket = sender_socket

    def fileno(self):
        return self.ssock.fileno()

    def do_read(self, fileno):
        data, sender = self.recvfrom(1024)

        if data:
            data = data.decode('utf-8')
            # "F7C027"  # WeMo Smart Switch
            # "F7C063"  # WeMo Mini

            if 'M-SEARCH' in data and  'urn:Belkin:device:controllee' in data:
                if DEVICE_TYPE == "F7C027" or DEVICE_TYPE == "F7C063":
                    time.sleep((random.randint(0, 2000) / 1000))
                    self.device.respond_to_search(sender)

            elif 'M-SEARCH' in data and 'urn:Belkin:device:insight:1' in data:
                if DEVICE_TYPE == "F7029V2":
                    dbg("Responding to search for F7029V2")
                    time.sleep((random.randint(0, 2000) / 1000))
                    pprint.pprint(sender)
                    self.device.respond_to_search(sender)

            elif 'M-SEARCH' in data and'urn:Belkin:device:sensor' in data:
                if DEVICE_TYPE == "F7C028":
                    dbg("Responding to search for sensor")
                    time.sleep((random.randint(0, 2000) / 1000))
                    self.device.respond_to_search(sender)

            else:
                pass

    #Receive network data
    def recvfrom(self, size):
        if self.TIMEOUT:
            self.ssock.setblocking(0)
            ready = select.select([self.ssock], [], [], self.TIMEOUT)[0]
        else:
            self.ssock.setblocking(1)
            ready = True

        try:
            if ready:
                return self.ssock.recvfrom(size)
            else:
                return False, False
        except Exception as e:
            dbg(e)
            return False, False

    def add_device(self, device):
        self.device = device
        dbg("UPnP broadcast listener: new device registered")




# MAIN


# Set up our singleton for polling the sockets for data ready
p = poller()

# Set up our singleton listener for UPnP broadcasts
u = upnp_broadcast_responder()
u.init_socket()

# Add the UPnP broadcast listener to the poller so we can respond
# when a broadcast is received.
p.add(u)

# Create our WeMo
wemo(switch_name, u, p, interface_ip, 46167)

while True:
    # Allow time for a ctrl-c to stop the process
    p.poll(100)
    time.sleep(0.1)

