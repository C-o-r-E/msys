import RPi.GPIO as GPIO
import MFRC522
import signal
import sys
from time import sleep
from gatekeeper import Gatekeeper


if sys.version_info[0] < 3:
    raise "Python 3.x required to run"



reader = MIFAREReader = MFRC522.MFRC522()

door = Gatekeeper('http://192.168.1.100:8000/members/')

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
    very sleepy
    """
    
    if door.authenticate(uid):
        #open
        door.update_cache(uid)
        
    else:
        #we might want to inform the user that they were rejected
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
            uid += hex(byte)[2:]
        request_access(uid)
    else:
        #print("PICC_AntiColl error: {}".format(status))
        #break
        pass
    
    sleep(1)
    
