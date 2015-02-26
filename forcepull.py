import os

os.system("git fetch --all")
os.system("git reset --hard origin/master")

print "Pulled"
