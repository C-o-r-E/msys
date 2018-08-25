#!/usr/bin/python3

if sys.version_info[0] < 3:
    raise "Python 3.x required to run"

import RPi.GPIO as GPIO

import signal
import sys
import signal
import json
import os
from time import sleep
from gatekeeper import Gatekeeper
import client_MFRC522

from typing import NoReturn

CONFIG_DOOR_OPEN_TIME = 2
CONFIG_BASE_URL = 'http://msys.heliosmakerspace.ca/members/'
CONFIG_PIN_LOCK = 11
CONFIG_POLL_DELAY = 1

def unlock():
    GPIO.output(CONFIG_PIN_LOCK, 1)

def lock():
    GPIO.output(CONFIG_PIN_LOCK, 0)
    
def cleanup(signal, frame):
    print("cleaning up...")
    lock()
    GPIO.cleanup()
    print("done!")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(CONFIG_PIN_LOCK, GPIO.OUT)



#attempt opening config file
base = os.path.dirname(os.path.abspath(__file__))
cfg_path = f"{base}/config_msys_client.json"

try:
    f = open(cfg_path)
    data = json.load(f)
    f.close()
    if 'door_open_time' in data:
        CONFIG_DOOR_OPEN_TIME = data['door_open_time']
    if 'base_url' in data:
        CONFIG_BASE_URL = data['base_url']
    if 'gpio_lock' in data:
        CONFIG_PIN_LOCK = data['gpio_lock']
    if 'poll_delay' in data:
        CONFIG_PIN_LOCK = data['poll_delay']
except FileNotFoundError as e:
    print(f"error opening file: [{e}]"
    print("using default settings")


door = Gatekeeper(CONFIG_BASE_URL)


def request_access(uid: str): -> NoReturn
    """
    Attempt to authenticate a given uid then unlock the door if accesss is allowed
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

handle_MFRC522_blocking(request_access, CONFIG_POLL_DELAY)
