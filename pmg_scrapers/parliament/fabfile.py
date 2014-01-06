from __future__ import with_statement
from fabric.api import *


def server():
    """
    To access this server via SSH:
        ssh -v -i ~/.ssh/aws_code4sa.pem ubuntu@54.194.55.6
    Logs can be found at:
        tail -n 100 /home/ubuntu/spider.log
    """

    env.hosts = ['54.194.55.6']
    env.envname = 'server'
    env.user = 'ubuntu'
    env.group = 'ubuntu'
    env.key_filename = '~/.ssh/aws_code4sa.pem'


def setup():
    """
    Install dependencies and create an application directory.
    """

    # update locale
    sudo('locale-gen en_ZA.UTF-8')

    # install pip
    sudo('apt-get install python-pip')
    sudo('apt-get install htop')

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % '/home/ubuntu/parliament').failed:
            # create project folder
            sudo('mkdir -p /home/ubuntu/parliament')
            sudo('mkdir -p /mnt/archive')

    # clear pip's cache
    with settings(warn_only=True):
        sudo('rm -r /tmp/pip-build-root')

    # install the necessary Python packages
    sudo('pip install simplejson')
    sudo('pip install requests')
    sudo('pip install xmltodict')
    sudo('pip install BeautifulSoup4')


def deploy():
    """
    Upload our script to the server.
    """

    # upload the source tarball to the temporary folder on the server
    put('spider.py', '/tmp/spider.py')
    sudo('mv -f /tmp/spider.py /home/ubuntu/parliament/spider.py')

    # clean out old logfiles
    with settings(warn_only=True):
        sudo('rm /home/ubuntu/debug.log*')
        sudo('rm /home/ubuntu/error.log*')


def download_archive():

    # create a tarball of our package
    with cd("/mnt"):
        sudo('tar -czf archive.tar.gz archive/')

    # upload the source tarball to the temporary folder on the server
    get('/mnt/archive.tar.gz')

    local('tar xzf ' + env.host + '/archive.tar.gz')

    # now that all is set up, delete the tarball again
    sudo('rm /mnt/archive.tar.gz')


def clear():
    """
    Clear state saving files and content, so the script can be restarted.
    """

    sudo("rm -r ~/parliament/")
    sudo("rm -r /mnt/archive/")
    sudo("mkdir ~/parliament")
    sudo("mkdir /mnt/archive")

## run spider with:
#    cd parliament
#    sudo nohup python spider.py &

# rsync --progress --partial --rsh="ssh -i /Users/petrus/.ssh/aws_code4sa.pem" ubuntu@54.194.55.6:/home/ubuntu/archive.tar.gz /Users/petrus/Desktop/archive.tar.gz