from __future__ import with_statement
from fabric.api import *


def staging():
    """
    Env parameters for the staging environment.
    """

    # env.hosts = ['54.229.255.34']
    env.hosts = ['ec2-54-194-122-94.eu-west-1.compute.amazonaws.com']
    env.envname = 'staging'
    env.user = 'ubuntu'
    env.group = 'ubuntu'
    env.key_filename = '~/.ssh/aws_code4sa.pem'
    env['config_dir'] = 'config_staging'
    print("STAGING ENVIRONMENT\n")


def restart():

    sudo('service nginx restart')


def setup():
    """
    Install dependencies and create an application directory.
    """

    with settings(warn_only=True):
        sudo('service nginx stop')

    # update locale
    sudo('locale-gen en_ZA.UTF-8')

    # install packages
    sudo('apt-get install build-essential python python-dev')
    sudo('apt-get install python-pip')

    # TODO: setup virtualenv

    # create application directory if it doesn't exist yet
    code_dir = '/var/www/test'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            # create project folder
            sudo('mkdir -p /var/www/test')
            sudo('mkdir -p /var/www/test/static')

    # clear pip's cache
    with settings(warn_only=True):
        sudo('rm -r /tmp/pip-build-root')

    # install the necessary Python packages
    put('requirements/base.txt', '/tmp/base.txt')
    put('requirements/production.txt', '/tmp/production.txt')
    sudo('pip install -r /tmp/production.txt')

    # install nginx
    sudo('apt-get install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    sudo('service nginx start')


def configure():
    """
    Upload config files, and restart server.
    """

    with settings(warn_only=True):
        sudo('stop uwsgi')
        sudo('rm /etc/nginx/sites-enabled/default')

    # upload nginx server block (virtualhost)
    put('test.conf', '/tmp/test.conf')
    sudo('mv /tmp/test.conf /var/www/test/test.conf')
    with settings(warn_only=True):
        sudo('ln -s /var/www/test/test.conf /etc/nginx/conf.d/')
    sudo('/etc/init.d/nginx restart')

    # upload uwsgi config
    put('uwsgi.ini', '/tmp/uwsgi.ini')
    sudo('mv /tmp/uwsgi.ini /var/www/test/uwsgi.ini')

    # make directory for uwsgi's log
    with settings(warn_only=True):
        sudo('mkdir -p /var/log/uwsgi')

    # upload upstart configuration for uwsgi 'emperor', which spawns uWSGI processes
    put('uwsgi.conf', '/tmp/uwsgi.conf')
    sudo('mv /tmp/uwsgi.conf /etc/init/uwsgi.conf')

    sudo('mkdir -p /etc/uwsgi/vassals')
    with settings(warn_only=True):
        # create symlink for emperor to find config file
        sudo('ln -s /var/www/test/uwsgi.ini /etc/uwsgi/vassals')

    sudo('chown -R www-data:www-data /var/log/uwsgi')
    sudo('chown -R www-data:www-data /var/www/test')

    sudo('start uwsgi')


def deploy():

    put('test.py', '/tmp/test.py')
    sudo('mv /tmp/test.py /var/www/test/test.py')

    # ensure user www-data has access to the application folder
    sudo('chown -R www-data:www-data /var/www/test')
    sudo('chmod -R 775 /var/www/test')



def deploy_backend():
    """
    Upload our package to the server, unzip it, and restart apache.
    """

    # create a tarball of our package
    local('tar -czf pmg_backend.tar.gz pmg_backend/', capture=False)
    local('tar -czf uploads.tar.gz instance/uploads/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('pmg_backend.tar.gz', '/tmp/pmg_backend.tar.gz')
    put('uploads.tar.gz', '/tmp/uploads.tar.gz')

    # enter application directory and unzip
    with cd('/var/www/pmgbilltracker'):
        sudo('tar xzf /tmp/pmg_backend.tar.gz')
        sudo('tar xzf /tmp/uploads.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /tmp/pmg_backend.tar.gz')
    sudo('rm /tmp/uploads.tar.gz')
    local('rm pmg_backend.tar.gz')
    local('rm uploads.tar.gz')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/pmg_backend/debug.log*')

    # ensure that apache user has access to all files
    sudo('chmod -R 770 /var/www/pmgbilltracker/pmg_backend')
    sudo('chmod -R 770 /var/www/pmgbilltracker/instance')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker/pmg_backend')
    sudo('chown -R ' + env.user + ':www-data /var/www/pmgbilltracker/instance')

    # and finally reload the application
    sudo('/etc/init.d/apache2 reload')


def deploy_frontend():
    """
    Upload our package to the server, unzip it, and restart apache.
    """

    # create a tarball of our package
    local('tar -czf pmg_frontend.tar.gz pmg_frontend/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('pmg_frontend.tar.gz', '/tmp/pmg_frontend.tar.gz')

    # turn off apache
    with settings(warn_only=True):
        sudo('/etc/init.d/apache2 stop')

    # enter application directory
    with cd('/var/www/pmgbilltracker'):
        # and unzip new files
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

    # and finally reload the application
    sudo('/etc/init.d/apache2 start')