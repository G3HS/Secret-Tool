#!/usr/bin/python
import requests
import json

r = requests.get('https://api.github.com/repos/thekaratekid552/Secret-Tool/releases')
latestRelease = r.json()[0]

if "assets" in latestRelease:
    for asset in latestRelease['assets']:
        print (latestRelease["tag_name"]+"~"+asset['name'] + ": " + str(asset['download_count']) +" downloads")