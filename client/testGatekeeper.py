import unittest
from gatekeeper import Gatekeeper
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process, Lock
from time import sleep
import json
import os

class dummyserver(BaseHTTPRequestHandler):

    reply = b"TEST"
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(dummyserver.reply)

    def do_POST(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(dummyserver.reply)
        
        

address = ('', 4125)

def doSrv():
    httpd = HTTPServer(address, dummyserver)
    httpd.timeout = 5
    httpd.handle_request()
    httpd.server_close()

class TestMissingServer(unittest.TestCase):

    def testAuth(self):
        g = Gatekeeper("http://127.0.0.2:4125")
        ret = g.authenticate("beefcafe")
        self.assertFalse(ret)

class TestAuthGood(unittest.TestCase):

    the_lock = Lock()

    def testAuthGood(self):
        dummyserver.reply = b"Granted"
        p = Process(target=doSrv)
        p.start()
        sleep(1)
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.authenticate("beefcafe")
        self.assertTrue(ret)

class TestAuthBad(unittest.TestCase):

    def testAuthBad(self):
        dummyserver.reply = b"Denied"
        p = Process(target=doSrv)
        p.start()
        sleep(1)
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.authenticate("beefcafe")
        self.assertFalse(ret)

class TestCache(unittest.TestCase):

    pos_data = {}
    neg_data = {}
    
    @classmethod
    def setUpClass(cls):
        days = ["mon", "tues", "wed", "thurs", "fri",
                "sat", "sun"]

        for d in days:
           cls.pos_data[d] = {"start": "00:00:00", "end":"23:59:59"}
           cls.neg_data[d] = {"start": "04:00:00", "end":"04:00:01"}

        #now create the db test files
        base = os.path.dirname(os.path.abspath(__file__))
        db_good = "{}/db/{}.json".format(base, "good.test")
        db_bad = "{}/db/{}.json".format(base, "bad.test")

        try:
            db_file = open(db_good, 'w')
            #db_file.write(json.dumps(cls.pos_data))
            json.dump(cls.pos_data, db_file)
            db_file.close()

            db_file = open(db_bad, 'w')
            #db_file.write(json.dumps(cls.neg_data))
            json.dump(cls.pos_data, db_file)
            db_file.close()
        except Exception as err:
            print("Error writing test DB files")
            print("err: [{}]".format(err))
            raise

    def test_json_pos(self):
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.json_has_access_now(json.dumps(TestCache.pos_data))
        self.assertTrue(ret)

    def test_json_neg(self):
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.json_has_access_now(json.dumps(TestCache.neg_data))
        self.assertFalse(ret)

    def test_cache_positive(self):
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.auth_from_cache("good.test")
        self.assertTrue(ret)

    def test_cache_negative(self):
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.auth_from_cache("bad.test")
        self.assertFalse(ret)
        

# REMOVE THIS
"""
class TestCoreyAuth(unittest.TestCase):

    def testCorey(self):
        g = Gatekeeper("http://msys.heliosmakerspace.ca/members/")
        uid = "b6afe558"
        ret = g.authenticate(uid)
        self.assertTrue(ret)
        g.update_cache(uid)
        cached = g.auth_from_cache(uid)
        self.assertTrue(cached)
"""

if __name__ == '__main__':
    unittest.main()
