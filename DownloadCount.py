#!/usr/bin/python
import requests
import json

r = requests.get('https://api.github.com/repos/thekaratekid552/Secret-Tool/releases')
obj = r.json()

for x in obj:
    if "assets" in x:
        for asset in x['assets']:
            print (x["tag_name"]+"\t"+asset['name'] + ": \t" + str(asset['download_count']) +" downloads")