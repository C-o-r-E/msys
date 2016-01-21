"""
This is some supe basic example code for invoking msys over HTTP

Stay tuned for more to come...
"""

import urllib.parse
import urllib.request

url = 'http://morg.123core.net/members/auth/'
values = {'id' : 'CF 95 3C A4'}

data = urllib.parse.urlencode(values)
data = data.encode('utf-8')

req = urllib.request.Request(url, data)
resp = urllib.request.urlopen(req)

text = resp.read()

if text == b'Granted':
    print('This is where we open the door')

else:
    print('You shall not pass')
