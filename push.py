import os

message = raw_input("Commit message: ")

os.system("git add -A")
os.system("git commit -m '"+message+"'")
os.system("git push")
