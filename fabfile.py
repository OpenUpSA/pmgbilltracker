from __future__ import with_statement
from fabric.api import *


def staging():
    """
    Env parameters for the staging environment.
    To access this server via SSH:
        ssh -v -i ~/.ssh/aws_code4sa.pem ubuntu@ec2-54-229-214-9.eu-west-1.compute.amazonaws.com
    Error logs can be found at:
        tail -n 100 /var/log/apache2/error.log
        tail -n 100 /var/www/pmgbilltracker/debug.log
    """

    env.hosts = ['ec2-54-229-214-9.eu-west-1.compute.amazonaws.com']
    env.envname = 'staging'
    env.user = 'ubuntu'
    env.group = 'ubuntu'
    env.key_filename = '~/.ssh/aws_code4sa.pem'
    env['config'] = 'instance/config.py'  # TODO: create separate config for this environment
    env['virtualhost'] = 'pmg_backend_apache'
    print("STAGING ENVIRONMENT\n")


def setup():
    """
    Install dependencies, create an application directory, and set up apache.
    """

    # update locale
    sudo('locale-gen en_ZA.UTF-8')

    # install pip
    sudo('apt-get install python-pip')

    # TODO: setup virtualenv

    # create application directory if it doesn't exist yet
    code_dir = '/var/www/pmgbilltracker'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            # create project folder
            sudo('mkdir -p /var/www/pmgbilltracker')
            sudo('mkdir /var/www/pmgbilltracker/instance')

    sudo('pip install Flask')
    sudo('pip install SQLAlchemy==0.7.10')
    sudo('pip install Flask-SQLAlchemy')
    sudo('pip install Flask-WTF==0.8.4')  # version 0.9.3 breaks support for flask-admin's file admin
    sudo('pip install Flask-Admin')
    sudo('pip install simplejson')

    # install apache2 and mod-wsgi
    sudo('apt-get install apache2')
    sudo('apt-get install libapache2-mod-wsgi')

    # ensure that apache user www-data has access to the application folder
    sudo('chmod -R 770 /var/www/pmgbilltracker')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker')

    # upload files to /tmp
    put(env['virtualhost'], '/tmp/pmg_backend_apache')
    put('wsgi.py', '/tmp/wsgi.py')

    # move files to their intended directories
    sudo('mv -f /tmp/pmg_backend_apache /etc/apache2/sites-available/pmg_backend_apache')
    sudo('mv -f /tmp/wsgi.py /var/www/pmgbilltracker/wsgi.py')

    # de-activate default site
    sudo('a2dissite default')

    # activate site
    sudo('a2ensite pmg_backend_apache')

    # restart apache
    sudo('/etc/init.d/apache2 reload')


def deploy():
    """
    Upload our package to the server, unzip it, and restart apache.
    """

    # create a tarball of our package
    local('tar -czf pmg_backend.tar.gz pmg_backend/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('pmg_backend.tar.gz', '/tmp/pmg_backend.tar.gz')

    # enter application directory and unzip
    with cd('/var/www/pmgbilltracker'):
        sudo('tar xzf /tmp/pmg_backend.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /tmp/pmg_backend.tar.gz')
    local('rm pmg_backend.tar.gz')

    # upload config file
    put(env['config'], '/tmp/config.py')
    sudo('mv -f /tmp/config.py /var/www/pmgbilltracker/instance/config.py')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/debug.log*')

    # ensure that apache user has access to all files
    sudo('chmod -R 770 /var/www/pmgbilltracker')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker')

    # and finally touch the wsgi.py file so that mod_wsgi triggers
    # a reload of the application
    sudo('/etc/init.d/apache2 reload')
    sudo('touch /var/www/pmgbilltracker/wsgi.py')
