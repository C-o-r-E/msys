#!/usr/bin/python3

"""
Something is weird about this library or maybe I'm not getting something.

It seems from the old code that we do the following:

a) make the PICC_REQIDL request
b) ignore its return value
c) do the anti-collision routine
d) extract a UID and ignore other statuses...

Going to start with this for now but it doesnt seem right...
"""


import MFRC522
from time import sleep
from typing import Callable

MIFAREReader = MFRC522.MFRC522()

def handle_MFRC522_blocking(uid_callback: Callable[[str], None], poll_delay: int) -> None:
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
            uid_callback(uid)
        else:
            #print("PICC_AntiColl error: {}".format(status))
            #break
            pass
        
        sleep(poll_delay)
