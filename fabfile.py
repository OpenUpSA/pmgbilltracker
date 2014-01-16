from __future__ import with_statement
from fabric.api import *


def staging():
    """
    Env parameters for the staging environment.
    """

    env.hosts = ['54.229.255.34']
    # env.hosts = ['ec2-54-194-122-94.eu-west-1.compute.amazonaws.com']
    env.envname = 'staging'
    env.user = 'ubuntu'
    env.group = 'ubuntu'
    env.key_filename = '~/.ssh/aws_code4sa.pem'
    env['config_dir'] = 'config_staging'
    print("STAGING ENVIRONMENT\n")
    return


def restart():

    sudo('service nginx restart')
    sudo('service uwsgi restart')
    return


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

    # clear pip's cache
    with settings(warn_only=True):
        sudo('rm -r /tmp/pip-build-root')

    # install the necessary Python packages
    put('requirements/base.txt', '/tmp/base.txt')
    put('requirements/production.txt', '/tmp/production.txt')
    put('requirements/scrapers.txt', '/tmp/scrapers.txt')
    sudo('pip install -r /tmp/production.txt')
    sudo('pip install -r /tmp/scrapers.txt')

    # install nginx
    sudo('apt-get install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    sudo('service nginx start')
    return


def run_scraper():
    
    # run scraper process
    # NOTE: the process keeps going even after manually closing the fabric session
    with cd('/var/www/pmgbilltracker/pmg_scrapers'):
        sudo('python main.py', pty=True)
    return


def download_database():

    # replace the local sqlite database with the latest copy from the server
    get('/var/www/pmgbilltracker/pmg_backend/pmgbilltracker.db', 'pmg_backend/pmgbilltracker.db')
    # download the scraper's latest log
    get('/var/www/pmgbilltracker/pmg_scrapers/debug.log', 'pmg_scrapers/debug.log')
    return


def deploy():

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d /var/www/pmgbilltracker").failed:
            # create project folder
            sudo('mkdir -p /var/www/pmgbilltracker')
    deploy_backend()
    deploy_frontend()
    deploy_scraper()
    return


def deploy_backend():
    """
    Upload our package to the server.
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

    sudo('touch /var/www/pmgbilltracker/pmg_backend/uwsgi.sock')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/pmg_backend/debug.log*')

    # ensure user www-data has access to the application folder
    sudo('chown -R www-data:www-data /var/www/pmgbilltracker')
    sudo('chmod -R 775 /var/www/pmgbilltracker')

    # and finally reload the application
    restart()
    return


def deploy_frontend():
    """
    Upload our package to the server, unzip it, and restart apache.
    """

    # create a tarball of our package
    local('tar -czf pmg_frontend.tar.gz pmg_frontend/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('pmg_frontend.tar.gz', '/tmp/pmg_frontend.tar.gz')

    # enter application directory
    with cd('/var/www/pmgbilltracker'):
        # and unzip new files
        sudo('tar xzf /tmp/pmg_frontend.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /tmp/pmg_frontend.tar.gz')
    local('rm pmg_frontend.tar.gz')

    sudo('touch /var/www/pmgbilltracker/pmg_frontend/uwsgi.sock')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/pmg_frontend/debug.log*')

    # ensure user www-data has access to the application folder
    sudo('chown -R www-data:www-data /var/www/pmgbilltracker')
    sudo('chmod -R 775 /var/www/pmgbilltracker')

    # and finally reload the application
    restart()
    return


def deploy_scraper():
    """
    Upload the scraper to the server.
    """

    # create a tarball of our package
    local('tar -czf pmg_scrapers.tar.gz pmg_scrapers/', capture=False)

    # upload the source tarball to the temporary folder on the server
    put('pmg_scrapers.tar.gz', '/tmp/pmg_scrapers.tar.gz')

    # enter application directory
    with cd('/var/www/pmgbilltracker'):
        # and unzip new files
        sudo('tar xzf /tmp/pmg_scrapers.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /tmp/pmg_scrapers.tar.gz')
    local('rm pmg_scrapers.tar.gz')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /var/www/pmgbilltracker/pmg_scrapers/debug.log*')

    # ensure user www-data has access to the application folder
    sudo('chown -R www-data:www-data /var/www/pmgbilltracker')
    sudo('chmod -R 775 /var/www/pmgbilltracker')
    return


def configure():
    """
    Upload config files, and restart server.
    """

    with settings(warn_only=True):
        sudo('stop uwsgi')

    with settings(warn_only=True):
        # disable default site
        sudo('rm /etc/nginx/sites-enabled/default')

    # upload nginx server blocks (virtualhost)
    put(env['config_dir'] + '/nginx_backend.conf', '/tmp/nginx_backend.conf')
    put(env['config_dir'] + '/nginx_frontend.conf', '/tmp/nginx_frontend.conf')
    sudo('mv /tmp/nginx_backend.conf /var/www/pmgbilltracker/nginx_backend.conf')
    sudo('mv /tmp/nginx_frontend.conf /var/www/pmgbilltracker/nginx_frontend.conf')

    with settings(warn_only=True):
        sudo('ln -s /var/www/pmgbilltracker/nginx_backend.conf /etc/nginx/conf.d/')
        sudo('ln -s /var/www/pmgbilltracker/nginx_frontend.conf /etc/nginx/conf.d/')

    # upload uwsgi config
    put(env['config_dir'] + '/uwsgi_backend.ini', '/tmp/uwsgi_backend.ini')
    put(env['config_dir'] + '/uwsgi_frontend.ini', '/tmp/uwsgi_frontend.ini')
    sudo('mv /tmp/uwsgi_backend.ini /var/www/pmgbilltracker/uwsgi_backend.ini')
    sudo('mv /tmp/uwsgi_frontend.ini /var/www/pmgbilltracker/uwsgi_frontend.ini')

    # make directory for uwsgi's log
    with settings(warn_only=True):
        sudo('mkdir -p /var/log/uwsgi')

    with settings(warn_only=True):
        sudo('mkdir -p /etc/uwsgi/vassals')

    # upload upstart configuration for uwsgi 'emperor', which spawns uWSGI processes
    put(env['config_dir'] + '/uwsgi.conf', '/tmp/uwsgi.conf')
    sudo('mv /tmp/uwsgi.conf /etc/init/uwsgi.conf')

    with settings(warn_only=True):
        # create symlinks for emperor to find config file
        sudo('ln -s /var/www/pmgbilltracker/uwsgi_backend.ini /etc/uwsgi/vassals')
        sudo('ln -s /var/www/pmgbilltracker/uwsgi_frontend.ini /etc/uwsgi/vassals')

    sudo('chown -R www-data:www-data /var/log/uwsgi')
    sudo('chown -R www-data:www-data /var/www/pmgbilltracker')

    # upload flask config
    put(env['config_dir'] + '/config_backend.py', '/tmp/config_backend.py')
    put(env['config_dir'] + '/config_frontend.py', '/tmp/config_frontend.py')
    sudo('mv /tmp/config_backend.py /var/www/pmgbilltracker/instance/config_backend.py')
    sudo('mv /tmp/config_frontend.py /var/www/pmgbilltracker/instance/config_frontend.py')

    # sudo('start uwsgi')
    # sudo('/etc/init.d/nginx restart')
    restart()
    return