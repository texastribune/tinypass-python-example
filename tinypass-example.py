import base64
import csv
import datetime
import hashlib
import hmac
import json
import requests

PRIVATE_KEY = '<your private key here>'
APPLICATION_ID = '<your application ID here>'

URL = '/r2/access/search'

message = bytes("GET {}").format(URL).encode('utf-8')
print ("message: {}".format(message))
secret = bytes(PRIVATE_KEY).encode('utf-8')
print ("secret: {}".format(secret))

# don't ask me why these substitutions are here:
signature = base64.b64encode(hmac.new(
    secret, message, digestmod=hashlib.sha256).digest()).replace(
            '+', '-').replace('/', '_').rstrip('=')

print ("signature: {}".format(signature))
auth_header = "{}:{}".format(APPLICATION_ID, signature)
print ('auth_header: {}'.format(auth_header))

url = 'https://api.tinypass.com{}'.format(URL)
print ("url: {}".format(url))

response = requests.get(url,
        headers={'Authorization': '{}'.format(auth_header)})

body = json.loads(response.text)
print (json.dumps(body['data'], sort_keys=True, indent=4))

data = body['data']
keys = data[0].keys()
keys.append('expires')


def convert_date(unix_date):
    if unix_date < 1:
        return 0
    return datetime.datetime.fromtimestamp(int(unix_date)).strftime(
            '%Y-%m-%d %H:%M:%S')

for item in data:
    try:
        expires = item['expires']
    except KeyError:
        expires = 0
    item['expires'] = convert_date(expires)
    item['created'] = convert_date(item['created'])

with open('file.csv', 'wb') as file:
    w = csv.DictWriter(file, keys)
    w.writeheader()
    w.writerows(data)
