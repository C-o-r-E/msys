"""
Gatekeeper

Represents a node where authentication is needed to provide access. Something like a door
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
import datetime
import time


class Gatekeeper():
    """
    The Gatekeeper object is an interface to an MSYS server for authentication of IDs
    """

    REQUEST_TIMEOUT = 2
    CACHE_STALE_T = 604800 # number of seconds in 7 days

    def __init__(self, server_url):
        self.request_timeout = self.REQUEST_TIMEOUT
        if server_url[-1] != '/':
            server_url += '/'
        self.auth_url = server_url + "auth/"
        self.weekly_url = server_url + "weekly_access/"

    def json_has_access_now(self, json_str):
        """
        Check the data in provided json string to see if it should have access now

        Returns True if the data indicates that access should be provided at the current
        time. Returns False if the current time is outside of start and end times for
        the current day. Returns False if there is a formatting error.
        """

        day2day = {'mon': 0,
                   'tues': 1,
                   'wed': 2,
                   'thurs': 3,
                   'fri': 4,
                   'sat': 5,
                   'sun': 6
                  }

        try:
            today = datetime.date.today().weekday()
            cur_time = datetime.datetime.now().time()
            data = json.loads(str(json_str))
            print("data = {}\n\n".format(data))
            for day, times in data.items():
                print("day = [{}] day2day: [{}]".format(today, day2day[day]))
                if today == day2day[day]:
                    start_t = datetime.datetime.strptime(times['start'], '%H:%M:%S').time()
                    end_t = datetime.datetime.strptime(times['end'], '%H:%M:%S').time()
                    print("{} <= {} and {} >= {}".format(start_t, cur_time, end_t, cur_time))
                    if start_t <= cur_time and end_t >= cur_time:
                        return True

        except ValueError:
            print("ValueError!!!one1! \njson_str = {}".format(json_str))
            return False

        return False

    def update_cache(self, rfid):
        """
        Update our local store of access info for the given RFID

        Asks the server for the most up to date access info. Overwrites the previous stored data.
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
            print("Timeout (weekly): ", err)
            return

        text = resp.read()
        
        #save the file
        base = os.path.dirname(os.path.abspath(__file__))
        db_path = "{}/db/{}.json".format(base, rfid)
        
        try:
            db_file = open(db_path, 'wb')
        except:
            print("error opening db file: ", db_path)
            return
            
        db_file.write(text)
        db_file.close()

    def auth_from_cache(self, rfid):
        """
        Check the local cache to see if we remember past access info
        
        Returns True if the id has access at this day/time according to the chached info
        """
        
        #can we open the file
        base = os.path.dirname(os.path.abspath(__file__))
        fname = "{}/db/{}.json".format(base, rfid)
        
        try:
            mtime = os.path.getmtime(fname)
            delta_t = time.time() - mtime
            if delta_t > self.CACHE_STALE_T:
                return False
        
            db_file = open(fname, 'r')
            print('Opened file in cache [{}]'.format(fname))
            data = db_file.read()
            db_file.close()
            return self.json_has_access_now(data)
        except FileNotFoundError:
            print('Could not open [{}]'.format(fname))
            return False
        

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
        except URLError as err:
            print("URLError: auth_url:[{}]".format(self.auth_url))
            print("URLError: {}".format(err))
            print("Falling back to local cache")
            cached = self.auth_from_cache(rfid)
            return cached
        except timeout as err:
            cached = self.auth_from_cache(rfid)
            return cached

        text = resp.read()

        t2 = perf_counter()

        print("Auth got [{}] in {} sec".format(text, t2-t1))

        if text == b'Granted':
            return True
