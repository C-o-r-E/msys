"""
Gatekeeper

Represents a node where authentication is needed to provide access. Something like an door 
lock controlled by RFID card. Gatekeeper is a client of MSYS that primarily relies on the 
server for making authentication decisions. However sometimes the server may be unavailable
and just like a friendly castle guard, will be able to remember people that have been seen before.

Gatekeeper will cache the results of the recent authentications.
"""
import json
import urllib.parse
import urllib.request
from urllib.error import URLError
from time import perf_counter
import os


class Gatekeeper():
    """
    The Gatekeeper object is an interface to an MSYS server for authentication of IDs
    """
        
    def __init__(self, server_url):
        self.request_timeout = 2
        self.auth_url = server_url + "auth/"
        self.weekly_url = server_url + "weekly_access/"
        
    def update_cache(self, rfid):
        """
        bleh
        """

        values = {'id' : rfid}
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8')
        req = urllib.request.Request(self.weekly_url, data)
        
        try:
            resp = urllib.request.urlopen(req, timeout=self.request_timeout)
        except URLError:
            print("Weekly TODO: log that the connection was rejected...")
            return
            
        except timeout as err:
            print("Weekly: timeout")
            return
            
        text = resp.read()
        
        #save the file
        base = os.path.dirname(os.path.abspath(__file__))
        db_path = "{}/db/{}.json".format(base, rfid)
        
        try:
            db_file = open(db_path, 'w')
        except:
            print("TODO: handle file error")
            return
            
        db_file.write(str(text))
        db_file.close()
        

    def authenticate(self, rfid):
        """
        Authenticate an ID

        Returns True if the server allows access for the ID or if the server is unavailable,
        will return True if the cache indicates the ID had recent access
        """
        print("Auth id: [{}]".format(rfid))

        values = {'id' : rfid}
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8')

        t1 = perf_counter()

        req = urllib.request.Request(self.auth_url, data)
        try:
            resp = urllib.request.urlopen(req, timeout=self.request_timeout)
        except URLError:
            print("TODO: log that the connection was rejected...")
            print("TODO: Look in cache")
            return False
        except timeout as err:
            print("TODO: Look in cache")
            return False

        text = resp.read()

        t2 = perf_counter()

        print("Auth got [{}] in {} sec".format(text, t2-t1))

        if text == b'Granted':
            return True
