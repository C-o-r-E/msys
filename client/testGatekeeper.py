import unittest
from gatekeeper import Gatekeeper
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process, Lock
from time import sleep

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
        ret = g.authenticate("0")
        self.assertFalse(ret)

class TestAuthGood(unittest.TestCase):

    the_lock = Lock()

    def testAuthGood(self):
        dummyserver.reply = b"Granted"
        p = Process(target=doSrv)
        p.start()
        sleep(1)
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.authenticate("0")
        self.assertTrue(ret)

class TestAuthBad(unittest.TestCase):

    def testAuthBad(self):
        dummyserver.reply = b"Denied"
        p = Process(target=doSrv)
        p.start()
        sleep(1)
        g = Gatekeeper("http://127.0.0.1:4125")
        ret = g.authenticate("0")
        self.assertFalse(ret)

class TestCoreyAuth(unittest.TestCase):

    def testCorey(self):
        g = Gatekeeper("http://msys.heliosmakerspace.ca/members/")
        uid = "b6afe558"
        ret = g.authenticate(uid)
        self.assertTrue(ret)
        g.update_cache(uid)
        cached = g.auth_from_cache(uid)
        self.assertTrue(cached)

if __name__ == '__main__':
    unittest.main()
