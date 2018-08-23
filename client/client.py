#!/usr/bin/python3

import RPi.GPIO as GPIO
import MFRC522
import signal
import sys
import signal
import json
import os
from time import sleep
from gatekeeper import Gatekeeper

CONFIG_DOOR_OPEN_TIME = 2
CONFIG_BASE_URL = 'http://msys.heliosmakerspace.ca/members/'

def unlock():
    GPIO.output(11, 1)

def lock():
    GPIO.output(11, 0)
    
def cleanup(signal, frame):
    print("cleaning up...")
    lock()
    GPIO.cleanup()
    print("done!")
    sys.exit(0)


if sys.version_info[0] < 3:
    raise "Python 3.x required to run"

signal.signal(signal.SIGINT, cleanup)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

reader = MIFAREReader = MFRC522.MFRC522()

#attempt opening config file
base = os.path.dirname(os.path.abspath(__file__))
cfg_path = "{}/config_msys_client.json".format(base)

try:
    f = open(cfg_path)
    data = json.load(f)
    f.close()
    if 'door_open_time' in data:
        CONFIG_DOOR_OPEN_TIME = data['door_open_time']
    if 'base_url' in data:
        CONFIG_BASE_URL = data['base_url']
except FileNotFoundError as e:
    print("error opening file: [{}]".format(e))
    print("using default settings")


door = Gatekeeper(CONFIG_BASE_URL)

"""
Something is weird about this library or maybe I'm not getting something.

It seems from the old code that we do the following:

a) make the PICC_REQIDL request
b) ignore its return value
c) do the anti-collision routine
d) extract a UID and ignore other statuses...

Going to start with this for now but it doesnt seem right...
"""

def request_access(uid):
    """
    TODO: write something useful
    """
    
    if door.authenticate(uid):
        #first open the door
        unlock()
        sleep(CONFIG_DOOR_OPEN_TIME)
        lock()
        #then update the cache
        door.update_cache(uid)
        
    else:
        #we might want to inform the user that they were rejected
        print('ID does not have access now')
        pass

while True:
    (status, data) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL) 
    if status == MIFAREReader.MI_OK:
        pass
    else:
        #print("PICC_REQIDL error: {}".format(status))
        #break
        pass #Need to look in to why an error is returned before being able to read the uid...



    (status, data) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        uid = ''
        for byte in data[:-1]:
            if byte < 16:
                uid += '0'
            uid += hex(byte)[2:]
        request_access(uid)
    else:
        #print("PICC_AntiColl error: {}".format(status))
        #break
        pass
    
    sleep(1)
    
