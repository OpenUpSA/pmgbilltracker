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
    with cd(env.project_dir):
        with prefix(env.activate):
            yield


def schedule_scraper():

    # schedule the scraper to run
    with settings(warn_only=True):
        sudo('rm ' + env.project_dir + '/pmg_scrapers/debug.log')
        sudo('touch ' + env.project_dir + '/pmg_scrapers/debug.log')

    sudo('echo "0 21 * * * python ' + env.project_dir + '/pmg_scrapers/main.py" > /tmp/cron.txt')
    sudo('crontab /tmp/cron.txt')
    return


def unschedule_scraper():

    sudo('crontab -r')
    return


def restart():
    sudo("supervisorctl restart pmg_backend")
    sudo("supervisorctl restart pmg_frontend")
    sudo('service nginx restart')
    return


def set_permissions():
    """
     Ensure that www-data has access to the application folder
    """

    sudo('chown -R www-data:www-data ' + env.project_dir)
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
        if run("test -d %s" % env.project_dir).failed:
            # create project folder
            sudo("git clone https://github.com/Code4SA/pmgbilltracker.git " + env.project_dir)
        if run("test -d %s/env" % env.project_dir).failed:
            # create virtualenv
            sudo('virtualenv --no-site-packages %s/env' % env.project_dir)

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


def configure():
    """
    Configure Nginx, supervisor & Flask. Then restart.
    """

    with settings(warn_only=True):
        # disable default site
        sudo('rm /etc/nginx/sites-enabled/default')

    # upload nginx server blocks
    put(env.config_dir + '/nginx.conf', '/tmp/nginx.conf')
    sudo('mv /tmp/nginx.conf %s/nginx_pmgbilltracker.conf' % env.project_dir)

    # link server blocks to Nginx config
    with settings(warn_only=True):
        sudo('ln -s %s/nginx_pmgbilltracker.conf /etc/nginx/conf.d/' % env.project_dir)

    # upload supervisor config
    put(env.config_dir + '/supervisor.conf', '/tmp/supervisor.conf')
    sudo('mv /tmp/supervisor.conf /etc/supervisor/conf.d/supervisor_pmgbilltracker.conf')
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

    # configure Flask
    with settings(warn_only=True):
        sudo('mkdir %s/instance' % env.project_dir)
    put(env.config_dir + '/config_backend.py', '/tmp/config_backend.py')
    put(env.config_dir + '/config_frontend.py', '/tmp/config_frontend.py')
    put(env.config_dir + '/config_backend_private.py', '/tmp/config_backend_private.py')
    put(env.config_dir + '/config_frontend_private.py', '/tmp/config_frontend_private.py')
    sudo('mv /tmp/config_backend.py ' + env.project_dir + '/instance/config_backend.py')
    sudo('mv /tmp/config_frontend.py ' + env.project_dir + '/instance/config_frontend.py')
    sudo('mv /tmp/config_backend_private.py ' + env.project_dir + '/instance/config_backend_private.py')
    sudo('mv /tmp/config_frontend_private.py ' + env.project_dir + '/instance/config_frontend_private.py')

    restart()
    return


def deploy():
    # create a tarball of our packages
    local('tar -czf pmg_backend.tar.gz pmg_backend/', capture=False)
    local('tar -czf pmg_frontend.tar.gz pmg_frontend/', capture=False)
    local('tar -czf pmg_scrapers.tar.gz pmg_scrapers/', capture=False)

    # upload the source tarballs to the server
    put('pmg_backend.tar.gz', '/tmp/pmg_backend.tar.gz')
    put('pmg_frontend.tar.gz', '/tmp/pmg_frontend.tar.gz')
    put('pmg_scrapers.tar.gz', '/tmp/pmg_scrapers.tar.gz')

    with settings(warn_only=True):
        sudo('service nginx stop')

    # enter application directory
    with cd(env.project_dir):
        # and unzip new files
        sudo('tar xzf /tmp/pmg_backend.tar.gz')
        sudo('tar xzf /tmp/pmg_frontend.tar.gz')
        sudo('tar xzf /tmp/pmg_scrapers.tar.gz')

    # now that all is set up, delete the tarballs again
    sudo('rm /tmp/pmg_backend.tar.gz')
    sudo('rm /tmp/pmg_frontend.tar.gz')
    sudo('rm /tmp/pmg_scrapers.tar.gz')
    local('rm pmg_backend.tar.gz')
    local('rm pmg_frontend.tar.gz')
    local('rm pmg_scrapers.tar.gz')

    set_permissions()
    restart()
    return
