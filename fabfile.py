from __future__ import with_statement
from fabric.api import *


def staging():
    """
    Env parameters for the staging environment.
    To access this server via SSH:
        ssh -v -i ~/.ssh/aws_code4sa.pem ubuntu@54.229.255.34
    Error logs can be found at:
        tail -n 100 /var/log/apache2/error.log
        tail -n 100 /var/www/pmgbilltracker/debug.log
    """

    env.hosts = ['54.229.255.34']
    env.envname = 'staging'
    env.user = 'ubuntu'
    env.group = 'ubuntu'
    env.key_filename = '~/.ssh/aws_code4sa.pem'
    env['config_dir'] = 'config_staging'
    print("STAGING ENVIRONMENT\n")


def install_dependencies():
    """
    Install dependencies and create an application directory.
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
            sudo('mkdir -p /var/www/pmgbilltracker/pmg_backend')
            sudo('mkdir -p /var/www/pmgbilltracker/pmg_frontend')
            sudo('mkdir /var/www/pmgbilltracker/instance')

    # clear pip's cache
    with settings(warn_only=True):
        sudo('rm -r /tmp/pip-build-root')

    # install the necessary Python packages
    sudo('pip install Flask')
    sudo('pip install SQLAlchemy==0.8.2')
    sudo('pip install Flask-SQLAlchemy==1.0')
    sudo('pip install Flask-Admin==1.0.7')
    sudo('pip install simplejson')
    sudo('pip install requests==2.0.1')

    # install apache2 and mod-wsgi
    sudo('apt-get install apache2')
    sudo('apt-get install libapache2-mod-wsgi')

    # ensure that apache user www-data has access to the application folder
    sudo('chmod -R 770 /var/www/pmgbilltracker')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker')


def configure():
    """
    Upload config files, and restart apache.
    """

    # upload files to /tmp
    put(env.config_dir + '/apache_backend.conf', '/tmp/apache_backend.conf')
    put(env.config_dir + '/apache_frontend.conf', '/tmp/apache_frontend.conf')
    put(env.config_dir + '/config_backend.py', '/tmp/config_backend.py')
    put(env.config_dir + '/config_frontend.py', '/tmp/config_frontend.py')
    put(env.config_dir + '/wsgi_backend.py', '/tmp/wsgi_backend.py')
    put(env.config_dir + '/wsgi_frontend.py', '/tmp/wsgi_frontend.py')
    put(env.config_dir + '/hosts', '/tmp/hosts')

    # move files to their intended directories
    sudo('mv -f /tmp/apache_backend.conf /etc/apache2/sites-available/apache_backend.conf')
    sudo('mv -f /tmp/apache_frontend.conf /etc/apache2/sites-available/apache_frontend.conf')
    sudo('mv -f /tmp/config_backend.py /var/www/pmgbilltracker/instance/config_backend.py')
    sudo('mv -f /tmp/config_frontend.py /var/www/pmgbilltracker/instance/config_frontend.py')
    sudo('mv -f /tmp/wsgi_backend.py /var/www/pmgbilltracker/wsgi_backend.py')
    sudo('mv -f /tmp/wsgi_frontend.py /var/www/pmgbilltracker/wsgi_frontend.py')
    sudo('mv -f /tmp/hosts /etc/hosts')

    # de-activate default site
    with settings(warn_only=True):
        sudo('a2dissite 000-default')

    # activate site
    sudo('a2ensite apache_backend.conf')
    sudo('a2ensite apache_frontend.conf')

    # restart apache
    sudo('/etc/init.d/apache2 reload')


def deploy_backend():
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

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/pmg_backend/debug.log*')

    # ensure that apache user has access to all files
    sudo('chmod -R 770 /var/www/pmgbilltracker/pmg_backend')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker/pmg_backend')

    # and finally touch the wsgi.py file so that mod_wsgi triggers
    # a reload of the application
    sudo('/etc/init.d/apache2 reload')
    sudo('touch /var/www/pmgbilltracker/wsgi_backend.py')


def deploy_frontend():
    """
    Upload our package to the server, unzip it, and restart apache.
    """

    # create a tarball of our package
    local('tar -czf pmg_frontend.tar.gz pmg_frontend/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('pmg_frontend.tar.gz', '/tmp/pmg_frontend.tar.gz')

    # enter application directory and unzip
    with cd('/var/www/pmgbilltracker'):
        sudo('tar xzf /tmp/pmg_frontend.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /tmp/pmg_frontend.tar.gz')
    local('rm pmg_frontend.tar.gz')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/pmg_frontend/debug.log*')

    # ensure that apache user has access to all files
    sudo('chmod -R 770 /var/www/pmgbilltracker/pmg_frontend')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker/pmg_frontend')

    # and finally touch the wsgi.py file so that mod_wsgi triggers
    # a reload of the application
    sudo('/etc/init.d/apache2 reload')
    sudo('touch /var/www/pmgbilltracker/wsgi_frontend.py')