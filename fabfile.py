from __future__ import with_statement
import sys
from fabric.api import *

try:
    from fabdefs import *
except ImportError:
    print "Ensure that you have a fabdefs.py in your directory. Copy fabdefs.py.example and use that as a template"
    sys.exit(1)

def restart():
    sudo("supervisorctl restart pmg_backend")
    sudo("supervisorctl restart pmg_frontend")


def deploy():
    with cd("/var/www/bills.pmg.org.za"):
        # run("git pull origin master")
        run("mv config_staging/config_backend.py instance/config_backend.py")
        run("mv config_staging/config_backend.py instance/config_frontend.py")
    restart()

#def run_scraper():
#
#    # run scraper process
#    # NOTE: the process keeps going even after manually closing the fabric session
#    with settings(warn_only=True):
#        sudo('rm /var/www/pmgbilltracker/pmg_scrapers/debug.log')
#        sudo('touch /var/www/pmgbilltracker/pmg_scrapers/debug.log')
#    with cd('/var/www/pmgbilltracker/pmg_scrapers'):
#        sudo('python main.py', pty=True)
#    return


