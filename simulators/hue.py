#!/usr/bin/env python
# Requires python3
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
import ast
import json

"""
This script can be used to emulate a Hue Briged and some number of connected light bulbs.
It currently only supports on/off/dim for a dimmable bulb and does not support hue/saturation.
I used a real outlet plug, Wireshark, and a LAN tap to watch SSDP traffic over the network. 
Then, wrote this script to simulate the device. It is meant to be run on a private LAN on a 
Raspberry Pi. It can also be used with Vagrant and Virtual Box on OSX. I wrote this at a 
previous job to allow us to test our system without actually having to have this device 
present. Admittedly, it is not great code but functional.
"""

if not os.geteuid() == 0:
    sys.exit('Script must be run as root')

parser = optparse.OptionParser()
parser.add_option('--macchanger', dest='macchanger', help='Write Mac Changer FIle', action='store_true')
parser.add_option('--debug', dest='debug', help='Debug Logging', action='store_true')
parser.add_option('--vagrant', dest='vagrant', help='Vagrant', action='store_true')
parser.add_option('--address', dest='address', help='IP Address', type="string")
parser.add_option('--lights', dest='numlights', help='Number of Lights', type="int", default=3)

(options, args) = parser.parse_args()

if options.macchanger:
    first_bits = "00:17:88:"
    last_bits = "%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    mac_address = first_bits + last_bits
    macchanger = ""
    if options.vagrant:
        macchanger = 'ACTION=="add", SUBSYSTEM=="net", KERNEL=="eth1" RUN+="/usr/bin/macchanger -m %s %s"' % (str(mac_address), '%k')
    else:
        macchanger = 'ACTION=="add", SUBSYSTEM=="net", KERNEL=="eth0" RUN+="/usr/bin/macchanger -m %s %s"' % (str(mac_address), '%k')
    text_file = open("/etc/udev/rules.d/70-macchanger.rules", "w")
    text_file.write(macchanger)
    text_file.close()
    sys.exit(1)


DEBUGSSDP = False
DEBUG = False

if options.debug:
    DEBUG = True


# 001788 is the hue mac range
first_bits = "00:17:88:"
last_bits = "%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

global_interface_ip = '0.0.0.0'

if options.vagrant:
    # we are running under vagrant
    switch_name = "eth1"

    proc = subprocess.Popen('ifconfig | grep -A 1 eth1', stdout=subprocess.PIPE, shell=True)
    tmp = proc.stdout.read()
    tmp = tmp.decode('utf-8')
    tmp = ' '.join(tmp.split())
    m = re.match('.*HWaddr ([A-z0-9:]+)\s', tmp)
    if m:
        mac_address = m.group(1)
        parts = mac_address.split(":")
        first_bits = "00:17:88:"
        last_bits = str(parts[3]) + ":" + str(parts[4]) + ":" + str(parts[5])
    m = re.match('.*inet addr:([0-9.]+)\s', tmp)
    if m:
        global_interface_ip = m.group(1)

else:
    # We are running on a Pi
    global_interface_ip = options.address
    if options.address is None:
        print("You must specify an IP address for yourHue device to use")
        sys.exit(1)

    octets = global_interface_ip.split('.')
    switch_name = "hue_" + str(octets[3])

global_mac_address = first_bits + last_bits
global_hue_bridge_id = first_bits + "FFFE" + last_bits
global_hue_bridge_id = global_hue_bridge_id.replace(":", "")
mac_part = global_mac_address
mac_part = mac_part.replace(":", "")
global_interface_ip = global_interface_ip.strip()
global_device_uuid = "2f402f80-da50-11e1-9b23-" + mac_part
global_device_serial_number = mac_part
global_username = "100000000000haham0mfeddadbadf00d"
global_numlights = options.numlights


octets = global_interface_ip.split('.')
if (len(octets) != 4):
    print("Invalid IP")
    sys.exit(1)


print("Hue Address : " + global_interface_ip)
print ("Hue Bridge ID : " + global_hue_bridge_id)
print("Number of lights : " + str(options.numlights))
print("Hue Bridge Username : " + global_username)
print("Interface Name: " + switch_name)

if not options.vagrant:
    # if running on a Pi, set up the interfaces

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
        ret = subprocess.check_call(
            ['ip', 'link', 'add', 'link', 'eth0', switch_name, 'address', global_mac_address, 'type', 'macvlan'],
            stdout=devnull, stderr=devnull)

    with open(os.devnull, 'wb') as devnull:
        ret = subprocess.check_call(['ifconfig', switch_name, global_interface_ip, 'netmask', '255.255.255.0'],
                                    stdout=devnull, stderr=devnull)

"""
This is the description.xml from a hue bridge
"""
SETUP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
<specVersion>
<major>1</major>
<minor>0</minor>
</specVersion>
<URLBase>http://%(ip_address)s:80/</URLBase>
<device>
<deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
<friendlyName>%(device_name)s</friendlyName>
<manufacturer>Royal Philips Electronics</manufacturer>
<manufacturerURL>http://www.philips.com</manufacturerURL>
<modelDescription>Philips hue Personal Wireless Lighting</modelDescription>
<modelName>Philips hue bridge 2015</modelName>
<modelNumber>BSB002</modelNumber>
<modelURL>http://www.meethue.com</modelURL>
<serialNumber>%(serial_number)s</serialNumber>
<UDN>uuid:%(device_uuid)s</UDN>
<presentationURL>index.html</presentationURL>
<iconList>
<icon>
<mimetype>image/png</mimetype>
<height>48</height>
<width>48</width>
<depth>24</depth>
<url>hue_logo_0.png</url>
</icon>
</iconList>
</device>
</root>
"""


def dbgSSDP(msg):
    global DEBUGSSDP
    if DEBUGSSDP:
        print(msg)
        sys.stdout.flush()


def dbg(msg):
    global DEBUG
    if DEBUG:
        print(msg)
        sys.stdout.flush()


def get_interface_for_ip(ip_address):
    """
    Gets the interface name corresponding to a local IP address
    :param ip_address:
    :return:
    """
    for iface in netifaces.interfaces():
        iface = iface.encode('ascii')
        iface = str(iface, 'utf-8')
        dbg("Interface found " + iface)
        if 'hue' in iface:
            ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            if ip == ip_address:
                return iface


class BasicLight(object):
    """
    Represents a dimmable Philips bulb which does not support hue/saturation/temperature
    """

    bulbType = "Dimmable light"
    lightname = "Hue white lamp"
    modelId = "LWB014"
    manufacturerName = "Philips"
    uniqueId = ""
    swVersion = "1.15.2_r19181"
    swConfigId = "D1D2055F"
    productId = "Philips-LWB014-1-A19DLv3"
    on = False
    bri = int(254)
    sat = int(254)
    hue = int(10000)
    alert = "none"
    reachable = True
    swUpdateState = "noupdates"
    lastInstall = "null"
    bulbNumber = 0

    def __init__(self, bulbType=bulbType,
                 lightname=lightname,
                 modelId=modelId,
                 manufacturerName=manufacturerName,
                 swVersion=swVersion,
                 swConfigId=swConfigId,
                 productId=productId,
                 on=on,
                 bri=bri,
                 alert=alert,
                 reachable=reachable,
                 swUpdateState=swUpdateState,
                 lastInstall=lastInstall,
                 bulbNumber=bulbNumber):
        # Create a random id for this lamp
        # Format : 00:17:88:01:02:f0:de:bc-0b
        first_bits = "00:17:88:01:02:"
        last_bits = "%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        postfix = "-0b"
        self.uniqueId = first_bits + last_bits + postfix


    def getLight(self):
        return self

    def getName(self):
        return self.lightname

    def getState(self):
        return self.on

    def getBri(self):
        return int(self.bri)

    def getBulbNumber(self):
        return self.bulbNumber

    def setBulbNumber(self, bulbNumber):
        self.bulbNumber = bulbNumber

    def setOn(self):
        self.on = True

    def setOff(self):
        self.on = False

    def setBri(self, bri):
        self.bri = int(bri)

    def setHue(self, hue):
        self.hue = hue

    def setSat(self, sat):
        self.sat = sat

    def setLightName(self, lightName):
        self.lightname = lightName

                            # the following are not valid for this bulb type
                            #'sat': self.sat,
                            #'hue': self.hue,
    def getLightDict(self):
        thisLight = {
                     'state': {
                            'on': self.on,
                            'bri': int(self.bri),
                            'alert': str(self.alert),
                            'reachable': self.reachable},
                     'swupdate': { 'state': str(self.swUpdateState),  'lastinstall': str(self.lastInstall)},
                     'type': str(self.bulbType),
                     'name': str(self.lightname),
                     'modelid': str(self.modelId),
                     'manufacturername': str(self.manufacturerName),
                     'uniqueid': str(self.uniqueId),
                     'swversion': str(self.swVersion),
                     'swconfigid': str(self.swConfigId),
                     'productid': str(self.productId),
        }
        return thisLight
    
    def getLightJson(self):
        thisLight = """{
                     'state': {
                            'on': self.on,
                            'bri': int(self.bri),
                            'alert': str(self.alert),
                            'reachable': self.reachable},
                     'swupdate': { 'state': str(self.swUpdateState),  'lastinstall': str(self.lastInstall)},
                     'type': str(self.bulbType),
                     'name': str(self.lightname),
                     'modelid': str(self.modelId),
                     'manufacturername': str(self.manufacturerName),
                     'uniqueid': str(self.uniqueId),
                     'swversion': str(self.swVersion),
                     'swconfigid': str(self.swConfigId),
                     'productid': str(self.productId),
        }"""
        return thisLight


class AdvancedLight(object):
    """
    Represents a dimmable Philips bulb which also supports hue/saturation/temperature
    """
    bulbType = "Extended color light"
    lightname = "Hue color lamp"
    modelId = "LCT001"
    manufacturerName = "Philips"
    uniqueId = ""
    swVersion = "5.50.1.19085"
    on = False
    bri = int(254)
    sat = int(254)
    hue = int(10000)
    ct = int(254)
    xy = [float(0.4571), float(0.4097)]
    effect = "none"
    colormode = "hs"
    alert = "none"
    reachable = True
    swUpdateState = "noupdates"
    lastInstall = "null"
    bulbNumber = 0

    def __init__(self, bulbType=bulbType,
                 lightname=lightname,
                 modelId=modelId,
                 manufacturerName=manufacturerName,
                 swVersion=swVersion,
                 on=on,
                 bri=bri,
                 hue=hue,
                 sat=sat,
                 ct=ct,
                 effect=effect,
                 colormode=colormode,
                 xy=xy,
                 alert=alert,
                 reachable=reachable,
                 swUpdateState=swUpdateState,
                 lastInstall=lastInstall,
                 bulbNumber=bulbNumber):
        # Create a random id for this lamp
        # Format : 00:17:88:01:02:f0:de:bc-0b
        first_bits = "00:17:88:01:02:"
        last_bits = "%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        postfix = "-0b"
        self.uniqueId = first_bits + last_bits + postfix

    def getLight(self):
        return self

    def getName(self):
        return self.lightname

    def getState(self):
        return self.on


    def getBulbNumber(self):
        return self.bulbNumber

    def setBulbNumber(self, bulbNumber):
        self.bulbNumber = bulbNumber

    def setOn(self):
        self.on = True

    def setOff(self):
        self.on = False

    def setBri(self, bri):
        self.bri = int(bri)

    def getBri(self):
        return int(self.bri)

    def setHue(self, hue):
        self.hue = hue

    def getHue(self):
        return int(self.hue)

    def setSat(self, sat):
        self.sat = sat

    def getSat(self):
        return int(self.sat)

    def setCt(self, ct):
        self.ct = ct

    def getCt(self):
        return int(self.ct)

    def setXy(self, xy):
        self.xy = xy

    def getXy(self):
        return int(self.xy)

    def setEffect(self, effect):
        self.effect = effect

    def getEffect(self):
        return int(self.effect)

    def setColormode(self, colormode):
        self.colormode = colormode

    def getColormode(self):
        return int(self.colormode)



    def setLightName(self, lightName):
        self.lightname = lightName

        # the following are not valid for this bulb type
        # 'sat': self.sat,
        # 'hue': self.hue,

    def getLightDict(self):
        thisLight = {
            'state': {
                'on': self.on,
                'bri': int(self.bri),
                'hue': int(self.hue),
                'sat': int(self.sat),
                'effect': self.effect,
                'ct': int(self.ct),
                'alert': str(self.alert),
                'colormode': str(self.colormode),
                'reachable': self.reachable},
            'swupdate': {'state': str(self.swUpdateState), 'lastinstall': str(self.lastInstall)},
            'type': str(self.bulbType),
            'name': str(self.lightname),
            'modelid': str(self.modelId),
            'manufacturername': str(self.manufacturerName),
            'uniqueid': str(self.uniqueId),
            'swversion': str(self.swVersion),
        }
        return thisLight

    def getLightJson(self):
        thisLight = """{
                     'state': {
                            'on': self.on,
                            'bri': int(self.bri),
                            'hue': int(self.hue),
                            'sat': int(self.sat),
                            'effect': self.effect,
                            'ct': int(self.ct),
                            'alert': str(self.alert),
                            'colormode': str(self.colormode),
                            'reachable': str(self.reachable)
                            },
                     'swupdate': { 'state': str(self.swUpdateState),  'lastinstall': str(self.lastInstall)},
                     'type': str(self.bulbType),
                     'name': str(self.lightname),
                     'modelid': str(self.modelId),
                     'manufacturername': str(self.manufacturerName),
                     'uniqueid': str(self.uniqueId),
                     'swversion': str(self.swVersion),
        }"""
        return thisLight


class Lights(object):
    """
    Represents a group of Philips lights on a Hue bridge
    """
    bulb_number = 0
    lights_dict = dict()
    lights_array = []

    def __init__(self):
        pass

    def addBasicLight(self):
        Lights.bulb_number += 1
        light = BasicLight()
        light.setBulbNumber(Lights.bulb_number)
        light.setLightName("Hue Bulb" + str(Lights.bulb_number))
        self.lights_array.append(light)

    def addAdvancedLight(self):
        Lights.bulb_number += 1
        light = AdvancedLight()
        light.setBulbNumber(Lights.bulb_number)
        light.setLightName("Hue Bulb" + str(Lights.bulb_number))
        self.lights_array.append(light)

    def getLightsJson(self):
        """
        We build our own JSON because the Hue expects some items to be quoted and others not.
        Also, the spacing of the JSON is different than what the JSON lib would provide
        :return:
        """
        lights_json = {}
        for light in self.lights_array:
            tmp_dict = {str(light.getBulbNumber()): light.getLightDict()}
            lights_json.update(tmp_dict)

        lights_json_str = str(lights_json)
        lights_json_str = lights_json_str.replace("\'", '"')
        lights_json_str = lights_json_str.replace('True', 'true')
        lights_json_str = lights_json_str.replace('False', 'false')
        lights_json_str = lights_json_str.replace(': ', ':')
        lights_json_str = lights_json_str.replace('"null"', 'null')
        lights_json_str = lights_json_str.replace(', ', ',')
        return lights_json_str

    def getLightsArray(self):
        return self.lights_array

    def getLightDict(self,lightId):
        for key in self.lights_dict.keys():
            if str(key) == str(lightId):
                return self.lights_dict[key]

    def getLightJson(self, lightId):
        """
        Again, building our own JSON
        :param lightId:
        :return:
        """
        for light in self.lights_array:
            if str(light.getBulbNumber()) == str(lightId):
                light_json = str(light.getLightDict())
                light_json = light_json.replace("\'", '"')
                light_json = light_json.replace('True', 'true')
                light_json = light_json.replace('False', 'false')
                light_json = light_json.replace(': ', ':')
                light_json = light_json.replace('"null"', 'null')
                light_json = light_json.replace(', ', ',')
                return light_json

    def getLightObj(self, bulbNumber):
        for light in self.lights_array:
            if str(light.getBulbNumber()) == str(bulbNumber):
                return light

    def setOn(self, lightId):
        light = self.getLightObj(lightId)
        light.setOn()
        return self.getLightJson(lightId)

    def setOff(self, lightId):
        light = self.getLightObj(lightId)
        light.setOff()
        return self.getLightJson(lightId)

    def setBri(self, lightId, bri):
        light = self.getLightObj(lightId)
        light.setBri(int(bri))
        return self.getLightJson(lightId)

    def setSat(self, lightId, sat):
        light = self.getLightObj(lightId)
        light.setSat(int(sat))
        return self.getLightJson(lightId)

    def setHue(self, lightId, hue):
        light = self.getLightObj(lightId)
        light.setHue(int(hue))
        return self.getLightJson(lightId)

    def setCt(self, lightId, ct):
        light = self.getLightObj(lightId)
        light.setCt(int(ct))
        return self.getLightJson(lightId)

class poller:
    """
    A simple utility class to wait for incoming data to be
    ready on a socket.
    """

    def __init__(self):
        if 'poll' in dir(select):
            self.use_poll = True
            self.poller = select.poll()
        else:
            self.use_poll = False
        self.targets = {}

    def add(self, target, fileno=None):
        if not fileno:
            fileno = target.fileno()
        if self.use_poll:
            self.poller.register(fileno, select.POLLIN)
        self.targets[fileno] = target

    def remove(self, target, fileno=None):
        if not fileno:
            fileno = target.fileno()
        if self.use_poll:
            self.poller.unregister(fileno)
        del (self.targets[fileno])

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


class upnp_device(object):
    """
    Base class for a generic UPnP device.
    """
    this_host_ip = global_interface_ip  # from the global above

    def __init__(self, listener, poller, port, root_url, server_version,
                 persistent_uuid, serial_number, other_headers=None):
        self.listener = listener
        self.poller = poller
        self.port = port
        self.root_url = root_url
        self.server_version = server_version
        self.persistent_uuid = persistent_uuid
        self.serial_number = serial_number

        self.other_headers = other_headers

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
                del (self.client_sockets[fileno])
            else:
                data = data.decode('utf-8')
                data = data.replace('\r', ' ')
                data = data.replace('\n', ' ')
                self.handle_request(data, sender, self.client_sockets[fileno])

    def handle_request(self, data, sender, socket):
        pass

    def get_name(self):
        return "unknown"

    def establish_keepalive(self):
        pass

    def respond_to_search(self, destination, my_socket, data):
        """
        These are Hue Bridge M-Search query responses
        :param destination:
        :param my_socket:
        :param data:
        :return:
        """
        dbgSSDP("Responding to M-SEARCH " + data)
        date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        location_url = self.root_url % {'ip_address': self.ip_address, 'port': 1900}
        message = (
            "HTTP/1.1 200 OK\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "EXT:\r\n"
            "CACHE-CONTROL: max-age=100\r\n"
            "LOCATION: %s\r\n"
            "SERVER: Linux/3.14.0 UPnP/1.0 IpBridge/1.21.0\r\n"
            "hue-bridgeid: %s\r\n"
            "ST: upnp:rootdevice\r\n"
            "USN: uuid:%s::upnp:rootdevice\r\n" % (location_url, global_hue_bridge_id.upper(),
                                                   global_device_uuid))
        message += "\r\n"
        my_socket.sendto(message.encode('utf-8'), destination)

        message = (
            "HTTP/1.1 200 OK\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "EXT:\r\n"
            "CACHE-CONTROL: max-age=100\r\n"
            "LOCATION: %s\r\n"
            "SERVER: Linux/3.14.0 UPnP/1.0 IpBridge/1.21.0\r\n"
            "hue-bridgeid: %s\r\n"
            "ST: uuid:%s\r\n"
            "USN: uuid:%s\r\n" % (location_url, global_hue_bridge_id.upper(),
                                  global_device_uuid, global_device_uuid))
        message += "\r\n"
        my_socket.sendto(message.encode('utf-8'), destination)

        message = (
            "HTTP/1.1 200 OK\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "EXT:\r\n"
            "CACHE-CONTROL: max-age=100\r\n"
            "LOCATION: %s\r\n"
            "SERVER: Linux/3.14.0 UPnP/1.0 IpBridge/1.21.0\r\n"
            "hue-bridgeid: %s\r\n"
            "ST: urn:schemas-upnp-org:device:basic:1\r\n"
            "USN: uuid:%s\r\n" % (location_url, global_hue_bridge_id.upper(),
                                  global_device_uuid))
        message += "\r\n"
        my_socket.sendto(message.encode('utf-8'), destination)


class upnp_broadcast_responder(object):
    """
    Listens for UPnP broadcasts
    """
    TIMEOUT = 0

    def __init__(self):
        self.devices = []

    def init_socket(self):
        ok = True
        self.ip = '239.255.255.250'
        self.port = 1900
        interface_name = get_interface_for_ip(global_interface_ip)
        try:
            # Set up server socket
            self.ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ssock.setsockopt(socket.SOL_SOCKET, 25, interface_name + '\0')
        except Exception as e:
            dbgSSDP("FAILED TO SET UP SOCKET")
            ok = False

        try:
            self.ssock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                                  socket.inet_aton(self.ip) + socket.inet_aton(global_interface_ip))

        except Exception as e:
            dbgSSDP('WARNING: Failed to join multicast group:')
            ok = False

        try:
            self.ssock.bind((self.ip, self.port))
        except Exception as e:
            dbgSSDP("FAILED TO BIND")
            ok = False

        if ok:
            dbgSSDP("Listening for UPnP broadcasts")

    def fileno(self):
        return self.ssock.fileno()

    def do_read(self, fileno):
        data, sender = self.recvfrom(1024)

        if data:
            data = str(data,'utf-8') 
            data = data.replace('\r', ' ')
            data = data.replace('\n', ' ')
            if 'ssdp:discover' in data and 'device:basic' in data:
                for device in self.devices:
                    time.sleep((random.randint(0, 100) / 1000))
                    device.respond_to_search(sender, self.ssock, data)
            else:
                pass

    # Receive network data
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
            dbgSSDP(e)
            return False, False

    def add_device(self, device):
        self.devices.append(device)
        dbgSSDP("UPnP broadcast listener: new device registered")


class hue(upnp_device):
    """
    A Hue Bridge
    """
    callback_ip = ""
    callback_port = ""
    persistent_uuid = ""
    seq_number = 0
    button_press = False
    lights = None

    def __init__(self, name, listener, poller, ip_address, port):
        self.serial_number = global_device_serial_number
        self.name = name
        self.ip_address = ip_address
        self.port = port
        persistent_uuid = global_device_uuid
        self.button_press = False

        other_headers = ['X-User-Agent: redsonic']
        upnp_device.__init__(self, listener, poller, port, "http://%(ip_address)s:80/description.xml",
                             "Unspecified, UPnP/1.0, Unspecified", persistent_uuid, self.serial_number,
                             other_headers=other_headers)
        dbg("Hue device '%s' ready on %s:%s" % (self.name, ip_address, port))

        self.lights = Lights()
        i = 0
        while i < global_numlights:
            self.lights.addAdvancedLight()
            i = i + 1


    def handle_request(self, data, sender, socket):


        generic_response_headers = ["HTTP/1.1 200 OK\r\n",
        "Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0\r\n",
        "Pragma: no-cache\r\n"
        "Expires: Mon, 1 Aug 2011 09:00:00 GMT\r\n",
        "Connection: close\r\n",
        "Access-Control-Max-Age: 3600\r\n",
        "Access-Control-Allow-Origin: *\r\n",
        "Access-Control-Allow-Credentials: true\r\n",
        "Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE, HEAD\r\n",
        "Access-Control-Allow-Headers: Content-Type\r\n",
        "Content-type: application/json\r\n"]

        dbg("REQUEST " + data)

        if 'PUT' in data and self.ip_address in data and "/lights/" in data and "/state" in data:
            dbg("******* HANDLING PUT REQUEST FOR LIGHT STATE ********")

            lightId = None
            m = re.match('.*/lights/([\d]+)/state', data)
            if m:
                lightId = m.group(1)

            if lightId:
                dbg("Found a match for this light ID" + lightId)
                m = re.match('.*(\\{[A-z0-9:,{}" ]+\\})', data)
                if m:
                    thisData = m.group(1)

                dbg("THISDATA " + thisData)

                on = None
                bri = None
                sat = None
                hue = None
                effect = None
                ct = None
                colormode = None
                xy = None

                # on/off
                m = re.match('.*"on":\s?([A-z]+).*', thisData)
                if m:
                    on = m.group(1)

                #{"bri":251,"on":true}
                m = re.match('.*"bri":\s?([0-9]+).*', thisData)
                if m:
                    bri = m.group(1)
                    bri = int(bri)

                # saturation
                m = re.match('.*"sat":\s?([0-9]+).*', thisData)
                if m:
                    dbg("GOT HERE IN SAT")
                    sat = m.group(1)
                    sat = int(sat)

                # hue
                m = re.match('.*"hue":\s?([0-9]+).*', thisData)
                if m:
                    dbg("GOT HERE IN HUE")
                    hue = m.group(1)
                    hue = int(hue)

                # ct
                m = re.match('.*"ct":\s?([0-9]+).*', thisData)
                if m:
                    dbg("GOT HERE IN CT")
                    ct = m.group(1)
                    ct = int(ct)
                    dbg("CT = " + str(ct))

                # colormode
                m = re.match('.*"colormode":\s?"([a-z]+)".*', thisData)
                if m:
                    dbg("GOT HERE IN COLORMODE")
                    colormode = m.group(1)

                # effect
                m = re.match('.*"effect":\s?"([a-z]+)".*', thisData)
                if m:
                    dbg("GOT HERE IN EFFECT")
                    effect = m.group(1)


                # xy  "xy":[0.4571,0.4097]
                m = re.match('.*"xy":\s?\[([0-9]+),\s?,([0-9]+)\].*', thisData)
                if m:
                    x = m.group(1)
                    x = int(x)
                    y = m.group(2)
                    y = int(y)



                response_data = '['


                if 'true' in on:
                    dbg("Turning on " + str(lightId))
                    self.lights.setOn(lightId)
                    dbg("Turning light on inside hue")
                    response_data += '{"success":{"/lights/%s/state/on":true}}' % str(lightId)

                elif 'false' in on:
                    dbg("Turning off " + str(lightId))
                    self.lights.setOff(lightId)
                    response_data += '{"success":{"/lights/%s/state/on":false}}' % str(lightId)

                if bri:
                    self.lights.setBri(lightId, int(bri))
                    dbg("Changing brightness " + str(lightId) + " to " + str(bri))
                    response_data += ',{"success": {"/lights/%s/state/bri":%d}}' % (str(lightId), int(bri))

                if hue:
                    self.lights.setHue(lightId, int(hue))
                    dbg("Changing hue " + str(lightId) + " to " + str(hue))
                    response_data += ',{"success": {"/lights/%s/state/hue":%d}}' % (str(lightId), int(hue))

                if sat:
                    self.lights.setSat(lightId, int(sat))
                    dbg("Changing saturation " + str(lightId) + " to " + str(sat))
                    response_data += ',{"success": {"/lights/%s/state/sat":%d}}' % (str(lightId), int(sat))

                if ct:
                    self.lights.setCt(lightId, int(ct))
                    dbg("Changing temperature " + str(lightId) + " to " + str(ct))
                    response_data += ',{"success": {"/lights/%s/state/ct":%d}}' % (str(lightId), int(ct))

                if colormode:
                    self.lights.setColormode(lightId, colormode)
                    dbg("Changing color mode " + str(lightId) + " to " + colormode)
                    response_data += ',{"success": {"/lights/%s/state/colormode":%s}}' % (str(lightId), str(colormode))

                if effect:
                    self.lights.setEffect(lightId, effect)
                    dbg("Changing effect " + str(lightId) + " to " + effect)
                    response_data += ',{"success": {"/lights/%s/state/effect":%s}}' % (str(lightId), str(effect))



                response_data += ']'
                message = (''.join(generic_response_headers) + "Content-Length: %d\r\n" % len(response_data))
                message += "\r\n" + response_data
                socket.send(message.encode('utf-8'))

        elif 'GET /control' in data and self.ip_address in data:

            print("THE DATA " + data)

            m = re.match(".*GET (/[\w]+/[0-9]+/[\w]+/[\w]+) HTTP.*", data)
            if m:
                data = m.group(1)

            #GET /control/1/on/true HTTP/1.1
            parts = data.split('/')

            # /control/1/on/true
            if len(parts) == 5:
                print("there are 5 parts")
                lightnumber = parts[2]
                action = parts[3]
                value = parts[4]

                if action == 'on':
                    print("action is on")
                    if value == 'true':
                        self.lights.setOn(lightnumber)
                    if value == 'false':
                        print("action is off")
                        self.lights.setOff(lightnumber)


            html = '<table border =1>'

            table_entry = """
            <tr><td>%(bulb_number)s</td>
            <td>%(light_name)s</td>
            <td>%(current_state)s</td>
            <td><a href="http://%(ip_address)s/control/%(bulb_number)s/on/%(new_state)s">Toggle State</a></td></tr>
            """
            for light in self.lights.getLightsArray():
                light.getBulbNumber()
                light.getName()
                light.getState()
                newState = 'false'
                if light.getState() == True:
                    newState = 'false'
                if light.getState() == False:
                    newState = 'true'

                html += table_entry % {'bulb_number': light.getBulbNumber(),
                                       'light_name': light.getName(),
                                       'current_state': light.getState(),
                                       'new_state': newState,
                                       'ip_address': self.ip_address
                                       }
            html += '</table>'

            message = ("HTTP/1.1 200 OK\r\n"
                       "CONTENT-LENGTH: %d\r\n"
                       "Content-type: text/html\r\n"
                       "\r\n"
                       "%s" % (len(html), html))
            socket.send(message.encode('utf-8'))


        elif 'GET /description.xml' in data and self.ip_address in data:
            dbg("Responding to description.xml request for %s" % self.name)
            xml = SETUP_XML % {'device_name': self.name, 'serial_number': global_device_serial_number,
                               'device_uuid': global_device_uuid, 'ip_address': self.ip_address}
            date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
            message = ("HTTP/1.1 200 OK\r\n"
                       "CONTENT-LENGTH: %d\r\n"
                       "Content-type: text/xml\r\n"
                       "\r\n"
                       "%s" % (len(xml), xml))

            #"Connection: Keep-Alive\r\n"
            socket.send(message.encode('utf-8'))

        elif 'GET /api' in data and self.ip_address in data and '/lights' in data and '/lights/' not in data:
            dbg("Responding to API request for lights")
            response_data = self.lights.getLightsJson()
            message = ''.join(generic_response_headers) + "Content-Length: %d\r\n" % len(response_data)
            message = message + "\r\n" + response_data
            dbg(message)
            socket.send(message.encode('utf-8'))


        elif 'GET /api' in data and self.ip_address in data and '/lights/' in data:
            dbg(data)
            dbg("this is a request for information about a specific lamp")
            lightId = None
            m = re.match(".*/lights/([0-9]+).*", data)
            if m:
                lightId = m.group(1)

            if lightId:
                dbg("got here")
                response_data = self.lights.getLightJson(lightId)
                dbg(response_data)
                message = ''.join(generic_response_headers) + "Content-Length: %d\r\n" % len(response_data)
                message = message + "\r\n" + response_data
                dbg(message)
                socket.send(message.encode('utf-8'))


        elif 'POST /api' in data and self.ip_address in data:

            #
            # this is a request for the user to press the button on the bridge 
            #
            if '"devicetype"' in data and self.button_press == False:
                dbg("Sending button press message")
                self.button_press = True
                response_data = '[{"error":{"type":101,"address":"","description":"link button not pressed"}}]'
                message = (''.join(generic_response_headers) + "Content-Length: %d\r\n" % len(response_data))
                message = message + "\r\n" + response_data
                dbg(message)
                socket.send(message.encode('utf-8'))

            #
            # this is the bridge sending the username back to the hub
            #
            if self.button_press == True and '"devicetype"' in data:
                dbg("Sending username to hub")
                response_data = '[{"success":{"username":"%s"}}]' % global_username
                message = (''.join(generic_response_headers) + "Content-Length: %d\r\n" % len(response_data))
                message = message + "\r\n" + response_data
                dbg(message)
                socket.send(message.encode('utf-8'))

        else:
            dbg("Fell through to the bottom")
            dbg(data)



# Set up our singleton for polling the sockets for data ready
p = poller()

# Set up our singleton listener for UPnP broadcasts
u = upnp_broadcast_responder()
u.init_socket()

# Add the UPnP broadcast listener to the poller so we can respond
# when a broadcast is received.
p.add(u)

hue(switch_name, u, p, global_interface_ip, 80)

dbg("Entering main loop")
while True:
    #try:
        # Allow time for a ctrl-c to stop the process
    p.poll(100)
    time.sleep(0.1)
    #except Exception as e:
    #    pprint.pprint("HERE " + str(e))
     #   dbg("hit exception, exiting")
    #    break
