#!/homeX/your_username/python27/bin/python27
import sys, os

# Add a custom Python path.
sys.path.insert(0, "/home3/onelivi2/python27")
sys.path.insert(13, "/home3/onelivi2/worship")

os.environ['DJANGO_SETTINGS_MODULE'] = 'worship.settings'
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")