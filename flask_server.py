#!/usr/bin/env python
# Requires python3
from flask import Flask
from flask import jsonify
from flask import make_response
import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BOARD)

"""
At a former job, I used a Raspberry PI and a couple of relay boards to
control power to IoT devices. Also, I soldered leads onto the devices sensors
so that I could simulate them sensing something. The tests, written in Groovy,
would connect to this service and our cloud service via Retrofit. Events simulated via
devices connected to this pi were verified to be passed up to the cloud service.   
"""


"""
ap relay numbers to board pins
"""
relays = dict([
    (1, 3), # relay 1, pin 3 
    (2, 5), # relay 2, pin 5 
    (3, 7), # etc... 
    (4, 11), 
    (5, 13),
    (6, 15),
    (7, 19),
    (8, 21)
])

#GPIO.setmode(GPIO.BCM)
#"""
#Map relay numbers to GPIO numbers 
#"""
#relays = dict([
#    (1, 2), # relay 1, pin 3 
#    (2, 3), # relay 2, pin 5 
#    (3, 17), # etc... 
#    (4, 27), 
#    (5, 22),
#    (6, 19),
#    (7, 21),
#    (8, 23)
#])

"""
Set the default state for each relay
"""
relays_defaults = dict([
    (1, 'off'), # relay 1, pin 3 
    (2, 'on'),  # relay 2, pin 5 
    (3, 'off'), # etc... 
    (4, 'off'), 
    (5, 'off'),
    (6, 'off'),
    (7, 'off'),
    (8, 'off')
])


app = Flask(__name__)

@app.route('/on/<int:relay>')
def relay_on(relay):
    #turn the relay on
    pin = relays[relay]
    GPIO.output(pin, GPIO.LOW)    
    return make_response(jsonify(operation='on'))

@app.route('/allon/')
def all_on():
    #turn all the relays on
    for relay in relays:
        pin = relays[relay]
        GPIO.output(pin, GPIO.LOW)    
    return make_response(jsonify(operation='allon'))

@app.route('/alloff/')
def all_off():
    #turn all the relays off 
    for relay in relays:
        pin = relays[relay]
        GPIO.output(pin, GPIO.HIGH)    
    return make_response(jsonify(operation='alloff'))


@app.route('/off/<int:relay>')
def relay_off(relay):
    # turn the relay off
    pin = relays[relay]
    GPIO.output(pin, GPIO.HIGH)    
    return make_response(jsonify(operation='off'))


@app.route('/state/<int:relay>')
def relay_status(relay):
    # get the relay state
    # TBD
    return make_response(jsonify(operation='state'))


@app.route('/pressandhold/<int:relay>/<int:duration>')
def relay_pressandhold(relay, duration):
    pin = relays[relay]
    GPIO.output(pin, GPIO.LOW)    
    time.sleep(duration)
    GPIO.output(pin, GPIO.HIGH)    
    return make_response(jsonify(operation='pressandhold'))

@app.route('/ping/<ipaddress>')
def ping(ipaddress):
    hostname = ipaddress
    response = os.system("ping -c 3 " + hostname)
    return make_response(jsonify(operation='ping', status=response))
      

try:
    for relay in relays:
        pin = relays[relay]
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)

    app.run(debug=True, host='0.0.0.0', port=80)
except KeyboardInterrupt:
    GPIO.cleanup()
except:
    print("Unknown exception occurred")
finally:
    GPIO.cleanup()
