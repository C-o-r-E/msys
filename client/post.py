"""
This is some supe basic example code for invoking msys over HTTP

Stay tuned for more to come...
"""

import urllib.parse
import urllib.request
from time import perf_counter
from socket import timeout

#url = 'http://morg.123core.net/members/auth/'
url = 'http://127.0.0.1:8000/members/auth/'
values = {'id' : '123'}

data = urllib.parse.urlencode(values)
data = data.encode('utf-8')

t1 = perf_counter()

req = urllib.request.Request(url, data)
resp = urllib.request.urlopen(req)

text = resp.read()

t2 = perf_counter()

if text == b'Granted':
    print('This is where we open the door')

else:
    print('You shall not pass')


print("Request took {} seconds".format(t2-t1))

###############################

url = 'http://127.0.0.1:8000/members/latency/'
values = {'time' : '1.7'}

data = urllib.parse.urlencode(values)
data = data.encode('utf-8')

t1 = perf_counter()

req = urllib.request.Request(url, data)

try:
    resp = urllib.request.urlopen(req, timeout=1)
except timeout as err:
    print("Timeout: {0}".format(err))


text = resp.read()

t2 = perf_counter()

print(text)
print("Request took {} seconds".format(t2-t1))

############################

url = 'http://127.0.0.1:8000/members/weekly_access/'
values = {'id' : '111'}

data = urllib.parse.urlencode(values)
data = data.encode('utf-8')

t1 = perf_counter()

req = urllib.request.Request(url, data)

try:
    resp = urllib.request.urlopen(req)
except timeout as err:
    print("Timeout: {0}".format(err))


text = resp.read()

t2 = perf_counter()

print(text)
print("Request took {} seconds".format(t2-t1))
