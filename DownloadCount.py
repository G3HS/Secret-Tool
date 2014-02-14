#!/usr/bin/python

import sys

try:
   import requests
except ImportError:
    print "Error: requests is not installed"
    print "Installing Requests is simple with pip:\n pip install requests"
    print "More info: http://docs.python-requests.org/en/latest/"
    exit(1)
import json


r = requests.get('https://api.github.com/repos/thekaratekid552/Secret-Tool/releases')
myobj = r.json()

latestRelease = myobj[0]

if "assets" in latestRelease:
    for asset in latestRelease['assets']:
        print (asset['name'] + ": " + str(asset['download_count']) +
               " downloads")
else:
    print "No data"
