from __future__ import with_statement
import sys
from fabric.api import *
from contextlib import contextmanager

try:
    from fabdefs import *
except ImportError:
    print "Ensure that you have a fabdefs.py in your directory. Copy fabdefs.py.example and use that as a template"
    sys.exit(1)


@contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.activate):
            yield


def restart():
    sudo("supervisorctl restart pmg_backend")
    sudo("supervisorctl restart pmg_frontend")
    return


def setup():

    # update locale
    sudo('locale-gen en_ZA.UTF-8')
    sudo('apt-get update')

    # install packages
    sudo('apt-get install build-essential')
    sudo('apt-get install python-pip supervisor')
    sudo('pip install virtualenv')

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % env.code_dir).failed:
            # create project folder
            sudo("git clone https://github.com/Code4SA/pmgbilltracker.git " + env.code_dir)
        if run("test -d %s/env" % env.code_dir).failed:
            # create virtualenv
            sudo('virtualenv --no-site-packages %s/env' % env.code_dir)

    # install the necessary Python packages
    with virtualenv():
        put('requirements/base.txt', '/tmp/base.txt')
        put('requirements/production.txt', '/tmp/production.txt')
        sudo('pip install -r /tmp/production.txt')

    # install nginx
    sudo('apt-get install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    sudo('service nginx start')
    return


def deploy():
    with cd(env.code_dir):
        run("git pull origin develop")
        sudo("mv config_staging/config_backend.py instance/config_backend.py")
        sudo("mv config_staging/config_frontend.py instance/config_frontend.py")
    restart()
    return


def schedule_scraper():

    # schedule the scraper to run
    with settings(warn_only=True):
        sudo('rm ' + env.code_dir + '/pmg_scrapers/debug.log')
        sudo('touch ' + env.code_dir + '/pmg_scrapers/debug.log')

    sudo('echo "0 21 * * * python ' + env.code_dir + '/pmg_scrapers/main.py" > /tmp/cron.txt')
    sudo('crontab /tmp/cron.txt')
    return


def unschedule_scraper():

    sudo('crontab -r')
    return
