#!/usr/bin/python
import urllib2
import json

r = urllib2.Request('https://api.github.com/repos/thekaratekid552/Secret-Tool/releases')
response = urllib2.urlopen(r)
obj = response.read()
obj = json.loads(obj)

ALLDL = 0
for x in obj[::-1]:
    if "assets" in x:
        print x["tag_name"]+":"
        print ("DL\t|\tOS")
        print ("--\t|\t--")
        totalDL = 0
        for asset in x['assets']:
            name = asset['name'].replace("Gen_III_Suite.","").replace(".zip","").replace("zip","")
            totalDL += asset['download_count']
            print str(asset['download_count']).zfill(4)+"\t|\t"+name
        print "Total Downloads: "+str(totalDL)
        ALLDL += totalDL
        print "~"*80
print "Total downloads of all versions: "+str(ALLDL)+"\n\n"