import httplib2
import urllib
import json
import sys

pin = sys.argv[1]
angle = sys.argv[2]
data = dict(angle=angle)
url = "http://192.168.1.17:7213/actuator/%s" % pin
print url
headers = {'content-type': 'application/x-www-form-urlencoded'}
body = urllib.urlencode(data)
h = httplib2.Http()
resp, content = h.request(url, method="POST", body=body, headers=headers)

print content