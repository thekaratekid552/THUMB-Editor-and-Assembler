import os
branch = str(raw_input("What branch to push to? "))
msg = str(raw_input("Please enter a commit reason: "))
os.system("git add -A")
os.system("git commit -m \"{0}\"".format(msg))
os.system("git push origin {0}".format(branch))
