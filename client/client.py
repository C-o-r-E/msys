import RPi.GPIO as GPIO
import MFRC522
import signal
import sys
from time import sleep


if sys.version_info[0] < 3:
    raise "Python 3.x required to run"



reader = MIFAREReader = MFRC522.MFRC522()


while True:
    ret = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL) 
    print(ret)
    ret = MIFAREReader.MFRC522_Anticoll()
    print(ret)
    
    sleep(1)
    
